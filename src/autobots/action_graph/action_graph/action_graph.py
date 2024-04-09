from typing import Dict, List, Set, Any, Optional

from fastapi import BackgroundTasks, HTTPException
from loguru import logger
from pydantic import HttpUrl

from src.autobots.action.action.action_doc_model import ActionDoc
from src.autobots.action.action.common_action_models import TextObj, TextObjs
from src.autobots.action.action.user_actions import UserActions
from src.autobots.action.action_market.user_actions_market import UserActionsMarket
from src.autobots.action_graph.action_graph.action_graph_doc_model import ActionGraphDoc
from src.autobots.action_graph.action_graph_result.action_graph_result_model_doc import ActionGraphResultDoc, \
    ActionGraphResultCreate, ActionGraphResultUpdate
from src.autobots.action_graph.action_graph_result.user_action_graph_result import UserActionGraphResult
from src.autobots.api.webhook import Webhook
from src.autobots.core.profiler.profiler import Profiler
from src.autobots.event_result.event_result_model import EventResultStatus


class ActionGraph:

    @staticmethod
    async def run_in_background(
            action_graph_doc: ActionGraphDoc,
            action_graph_input_dict: Dict[str, Any],
            user_actions: UserActions,
            user_actions_market: UserActionsMarket,
            user_action_graph_result: UserActionGraphResult,
            action_graph_result_id: Optional[str] = None,
            action_graph_node_id: Optional[str] = None,
            background_tasks: BackgroundTasks = None,
            webhook: Webhook | None = None,
    ) -> ActionGraphResultDoc | None:
        action_graph_result_doc: ActionGraphResultDoc | None = None
        if not action_graph_result_id:
            # Create initial Action Graph Result if not provided
            action_graph_doc.input = action_graph_input_dict
            action_graph_doc.output = {}
            action_graph_result_create: ActionGraphResultCreate = ActionGraphResultCreate(
                status=EventResultStatus.processing, result=action_graph_doc, is_saved=False
            )
            action_graph_result_doc = await user_action_graph_result.create_action_graph_result(action_graph_result_create)
            if webhook:
                await webhook.send(action_graph_result_doc.model_dump())
        else:
            # find and use Action Graph Result
            action_graph_result_doc = await user_action_graph_result.get_action_graph_result(action_graph_result_id)
            # Change status back to processing
            action_graph_result_update: ActionGraphResultUpdate = ActionGraphResultUpdate(status=EventResultStatus.processing)
            action_graph_result_doc = await user_action_graph_result.update_action_graph_result(
                action_graph_result_id,
                action_graph_result_update
            )

        if background_tasks:
            background_tasks.add_task(
                ActionGraph._run_as_background_task,
                user_actions,
                user_actions_market,
                action_graph_input_dict,
                action_graph_result_doc,
                user_action_graph_result,
                action_graph_node_id,
                webhook
            )
        else:
            action_graph_result_doc = await ActionGraph._run_as_background_task(
                user_actions,
                user_actions_market,
                action_graph_input_dict,
                action_graph_result_doc,
                user_action_graph_result,
                action_graph_node_id,
                webhook
            )

        return action_graph_result_doc

    @staticmethod
    async def _run_as_background_task(
            user_actions: UserActions,
            user_actions_market: UserActionsMarket,
            action_graph_input_dict: Dict[str, Any],
            action_graph_result_doc: ActionGraphResultDoc,
            user_action_graph_result: UserActionGraphResult,
            action_graph_node_id: Optional[str] = None,
            webhook: Webhook | None = None
    ):
        # TODO: check if action_graph_result_doc status is success, if success then return.
        # TODO: This behaviour should be accompanied by status change on action_graph_result_doc update

        # graph_map = action_graph_result_doc.result.graph
        # node_action_map = action_graph_result_doc.result.nodes
        # node_details_map = action_graph_result_doc.result.node_details
        # action_response: Dict[str, ActionDoc] = action_graph_result_doc.result.output
        # action_graph_input = TextObj.model_validate(action_graph_input_dict)

        # total_nodes = await ActionGraph.get_nodes(graph_map)
        # inverted_map = await ActionGraph.invert_map(graph_map)

        # review_required_nodes: List[str] = []

        # ACTION GRAPH RESULT - NODE RERUN
        if action_graph_node_id:
            action_graph_result_doc = await ActionGraph.run_node(
                user_actions,
                action_graph_input_dict,
                action_graph_result_doc,
                action_graph_node_id,
                user_action_graph_result,
                webhook
            )
        # ACTION GRAPH RESULT - GRAPH RUN / RERUN
        else:
            action_graph_result_doc = await ActionGraph.run_action_graph(
                user_actions,
                user_actions_market,
                action_graph_input_dict,
                action_graph_result_doc,
                user_action_graph_result,
                webhook
            )

        return action_graph_result_doc

    @staticmethod
    async def run_action_graph(
            user_actions: UserActions,
            user_actions_market: UserActionsMarket,
            action_graph_input_dict: Dict[str, Any],
            action_graph_result_doc: ActionGraphResultDoc,
            user_action_graph_result: UserActionGraphResult,
            webhook: Webhook | None = None
    ) -> ActionGraphResultDoc:
        graph_map = action_graph_result_doc.result.graph
        node_action_map = action_graph_result_doc.result.nodes
        node_details_map = action_graph_result_doc.result.node_details
        action_response: Dict[str, ActionDoc] = action_graph_result_doc.result.output
        # action_graph_input = TextObj.model_validate(action_graph_input_dict)

        total_nodes = await ActionGraph.get_nodes(graph_map)
        inverted_map = await ActionGraph.invert_map(graph_map)

        review_required_nodes: List[str] = []

        try:
            while len(action_response) + len(review_required_nodes) != len(total_nodes):
                for node, upstream_nodes in inverted_map.items():
                    if await ActionGraph.is_work_done([node], action_response) or \
                            not await ActionGraph.is_work_done(upstream_nodes, action_response):
                        continue
                    # Check if user review required
                    is_any_dependent_require_review = False
                    for upstream_node in upstream_nodes:
                        if (
                                node_details_map and
                                node_details_map.get(upstream_node) and
                                node_details_map.get(upstream_node).data.user_review_required and
                                not node_details_map.get(upstream_node).data.user_review_done
                        ):
                            review_required_nodes.append(upstream_node)
                            is_any_dependent_require_review = True
                    if is_any_dependent_require_review:
                        continue

                    if len(upstream_nodes) == 0:
                        # Run action with no dependency
                        action_result: ActionDoc = await ActionGraph.run_action(
                            user_actions,
                            user_actions_market,
                            node_action_map.get(node),
                            action_graph_input_dict
                        )
                        # action_result = await user_actions.run_action_v1(node_action_map.get(node), action_graph_input.model_dump())
                        action_response[node] = ActionDoc.model_validate(action_result)
                    else:
                        # Run action with at least 1 dependency
                        action_input = await ActionGraph.to_input(upstream_nodes, action_response)
                        action_result: ActionDoc = await ActionGraph.run_action(
                            user_actions,
                            user_actions_market,
                            node_action_map.get(node),
                            action_input.model_dump()
                        )
                        # action_result = await user_actions.run_action_v1(node_action_map.get(node), action_input.model_dump())
                        action_response[node] = ActionDoc.model_validate(action_result)

                        memory_profile = await Profiler.profile_memory()
                        logger.bind(memory_profile=memory_profile).info(f"Memory profile for Action run {action_result.name}:{action_result.version}")

                    # Update action result graph
                    action_graph_result_doc.result.output[node] = action_response[node]
                    action_graph_result_update: ActionGraphResultUpdate = ActionGraphResultUpdate(
                        result=action_graph_result_doc.result
                    )
                    action_graph_result_doc = await user_action_graph_result.update_action_graph_result(
                        action_graph_result_doc.id,
                        action_graph_result_update
                    )
                    if webhook:
                        await webhook.send(action_graph_result_doc.model_dump())

            # Update action result graph as success or waiting
            action_graph_result_update: ActionGraphResultUpdate | None
            if len(review_required_nodes) == 0:
                action_graph_result_update: ActionGraphResultUpdate = ActionGraphResultUpdate(
                    status=EventResultStatus.success
                )
            else:
                action_graph_result_update: ActionGraphResultUpdate = ActionGraphResultUpdate(
                    status=EventResultStatus.waiting
                )

            action_graph_result_doc = await user_action_graph_result.update_action_graph_result(
                action_graph_result_doc.id,
                action_graph_result_update
            )
            if webhook:
                await webhook.send(action_graph_result_doc.model_dump())
        except Exception as e:
            logger.bind(action_graph_id=action_graph_result_doc.result.id).error(f"Error while graph run, {str(e)}")

            # Update action result graph as error
            action_graph_result_update: ActionGraphResultUpdate = ActionGraphResultUpdate(
                status=EventResultStatus.error,
                error_message=TextObj(text=str(e))
            )
            action_graph_result_doc = await user_action_graph_result.update_action_graph_result(
                action_graph_result_doc.id,
                action_graph_result_update
            )
            if webhook:
                await webhook.send(action_graph_result_doc.model_dump())
        (logger.bind(action_graph_result_id=action_graph_result_doc.id,action_graph_id=action_graph_result_doc.result.id)
         .info("Completed Action Graph _run_as_background_task"))
        return action_graph_result_doc

    @staticmethod
    async def run_node(
            user_actions: UserActions,
            action_graph_input_dict: Dict[str, Any],
            action_graph_result_doc: ActionGraphResultDoc,
            action_graph_node_id: str,
            user_action_graph_result: UserActionGraphResult,
            webhook: Webhook | None = None
    ) -> ActionGraphResultDoc:
        action_response: Dict[str, ActionDoc] = action_graph_result_doc.result.output

        # Run action with no dependency
        node_action_doc = action_response.get(action_graph_node_id)
        action_result: ActionDoc = await ActionGraph.run_action_doc( # noqa F841
            user_actions,
            node_action_doc,
            action_graph_input_dict
        )
        # Update action result graph
        action_graph_result_update: ActionGraphResultUpdate = ActionGraphResultUpdate(
            result=action_graph_result_doc.result
        )
        action_graph_result_doc = await user_action_graph_result.update_action_graph_result(
            action_graph_result_doc.id,
            action_graph_result_update
        )
        if webhook:
            await webhook.send(action_graph_result_doc.model_dump())

        return action_graph_result_doc

    @staticmethod
    async def run_action(
            user_actions: UserActions,
            user_action_market: UserActionsMarket,
            action_id: str,
            action_graph_input_dict: Dict[str, Any]
    ) -> ActionDoc:
        exception = None
        try:
            action_result = await user_actions.run_action_v1(action_id, action_graph_input_dict)
            return action_result
        except HTTPException as e:
            exception = e
        try:
            action_result = await user_action_market.run_market_action(action_id, action_graph_input_dict)
            return action_result
        except Exception as e:
            raise HTTPException(405, f"{exception.detail} and {e}")

    @staticmethod
    async def run_action_doc(
            user_actions: UserActions,
            action_doc: ActionDoc,
            action_graph_input_dict: Dict[str, Any]
    ) -> ActionDoc:
        try:
            action_doc = await user_actions.run_action_doc(action_doc, action_graph_input_dict)
            return action_doc
        except Exception as e:
            logger.exception(str(e))
            raise

    @staticmethod
    async def get_nodes(graph: Dict[str, List[str]]) -> Set[str]:
        nodes: Set[str] = set()
        for key, values in graph.items():
            nodes.add(key)
            for val in values:
                nodes.add(val)
        return nodes

    @staticmethod
    async def invert_map(graph: Dict[str, List[str]]) -> Dict[str, List[str]]:
        inverted_map: Dict[str, List[str]] = {}

        nodes = await ActionGraph.get_nodes(graph)
        for node in nodes:
            inverted_map[node] = []

        for key, values in graph.items():
            for value in values:
                inverted_map[value] = inverted_map.get(value) + [key]

        return inverted_map

    @staticmethod
    async def is_work_done(values: List[str], action_response: Dict[str, Any]) -> bool:
        for value in values:
            if value not in action_response:
                return False
        return True

    @staticmethod
    async def to_input(values: List[str], action_response: Dict[str, ActionDoc]) -> TextObj:
        input_msg = ""
        for value in values:
            action_doc = action_response.get(value)
            action_outputs = action_doc.output
            try:
                # check if action_output is TextObjs
                action_outputs = TextObjs.model_validate(action_outputs)
                for action_output in action_outputs.texts:
                    # check for urls first TODO: Need for better solution
                    try:
                        potential_urls = action_output.text.split(",")
                        for potential_url in potential_urls:
                            url = HttpUrl(potential_url)
                            input_msg = input_msg + f"{url.unicode_string()},"
                    except Exception:
                        text_obj = TextObj.model_validate(action_output)
                        input_msg = f"{input_msg}\n## {action_doc.name}:\n{text_obj.text}\n\n"
            except Exception as e:
                logger.warning(f"Cannot convert to Input: {str(e)}")
            # if isinstance(action_outputs, TextObjs):
            #     for action_output in action_outputs.texts:
            #         if isinstance(action_output, TextObj):
            #             text_obj = TextObj.model_validate(action_output)
            #             input_msg = f"{input_msg}\n{text_obj.text}"
            # else:
            #     logger.warning("Cannot convert to Input")

        text_obj = TextObj(text=input_msg)
        return text_obj
