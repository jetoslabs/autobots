import json
from typing import Dict, List, Set, Any, Optional

from fastapi import BackgroundTasks, HTTPException
from loguru import logger
from openai.types.chat import ChatCompletionUserMessageParam
from pydantic import HttpUrl

from src.autobots.action.action.action_doc_model import ActionDoc
from src.autobots.action.action.common_action_models import MultiObj, TextObj, TextObjs
from src.autobots.action.action.user_actions import UserActions
from src.autobots.action.action_market.user_actions_market import UserActionsMarket
from src.autobots.action.action_type.action_map import ACTION_MAP
from src.autobots.action.action_type.action_text2text.action_text2text_llm_chat_openai_v2 import \
    ActionText2TextLlmChatOpenai
from src.autobots.action_graph.action_graph.action_graph_doc_model import ActionGraphDoc
from src.autobots.action_graph.action_graph_result.action_graph_result_model_doc import ActionGraphResultDoc, \
    ActionGraphResultCreate, ActionGraphResultUpdate
from src.autobots.action_graph.action_graph_result.user_action_graph_result import UserActionGraphResult
from src.autobots.api.webhook import Webhook
from src.autobots.conn.openai.openai_chat.chat_model import ChatReq
from src.autobots.core.logging.app_code import AppCode
from src.autobots.core.logging.log_binder import LogBinder
from src.autobots.core.profiler.profiler import Profiler
from src.autobots.data_model.context import Context
from src.autobots.event_result.event_result_model import EventResultStatus


class ActionGraph:

    @staticmethod
    async def run_in_background(
            ctx: Context,
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
        logger.bind(ctx=ctx).info("Action Graph Run started")
        action_graph_result_doc: ActionGraphResultDoc | None = None
        try:
            if not action_graph_result_id:
                logger.bind(ctx=ctx).info("Creating Action Graph Run")
                # Create initial Action Graph Result if not provided
                action_graph_doc.input = action_graph_input_dict
                action_graph_doc.output = {}
                action_graph_result_create: ActionGraphResultCreate = ActionGraphResultCreate(
                    status=EventResultStatus.processing, result=action_graph_doc, is_saved=False
                )
                action_graph_result_doc = await user_action_graph_result.create_action_graph_result(
                    action_graph_result_create)
                logger.bind(ctx=ctx, action_graph_result_doc=action_graph_result_doc).info("Created Action Graph Run")
                if webhook:
                    await webhook.send(action_graph_result_doc.model_dump())
            else:
                logger.bind(ctx=ctx).info("Find and use Action Graph Result")
                # find and use Action Graph Result
                action_graph_result_doc = await user_action_graph_result.get_action_graph_result(action_graph_result_id)
                # Change status back to processing
                logger.bind(ctx=ctx).info("Updating status of Action Graph Result to processing")
                action_graph_result_update: ActionGraphResultUpdate = ActionGraphResultUpdate(
                    status=EventResultStatus.processing)
                action_graph_result_doc = await user_action_graph_result.update_action_graph_result(
                    action_graph_result_id,
                    action_graph_result_update
                )

            if background_tasks:
                logger.bind(ctx=ctx).info("Starting background tasks")
                background_tasks.add_task(
                    ActionGraph._run_as_background_task,
                    ctx,
                    user_actions,
                    user_actions_market,
                    action_graph_input_dict,
                    action_graph_result_doc,
                    user_action_graph_result,
                    action_graph_node_id,
                    webhook
                )
            else:
                logger.bind(ctx=ctx).info("Running background tasks as method")
                action_graph_result_doc = await ActionGraph._run_as_background_task(
                    ctx,
                    user_actions,
                    user_actions_market,
                    action_graph_input_dict,
                    action_graph_result_doc,
                    user_action_graph_result,
                    action_graph_node_id,
                    webhook
                )

            return action_graph_result_doc
        except Exception as e:
            bind_dict = (LogBinder().with_app_code(AppCode.ACTION_GRAPH_RUN)
                         .with_action_graph_id(action_graph_doc.id)
                         .with_action_graph_run_id(action_graph_result_doc.id)
                         .get_bind_dict())
            logger.bind(ctx=ctx, **bind_dict).error(f"ActionGraph run failed due to {e}")
            raise

    @staticmethod
    async def _run_as_background_task(
            ctx: Context,
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

        # ACTION GRAPH RESULT - NODE RERUN
        if action_graph_node_id:
            logger.bind(ctx=ctx, action_graph_node_id=action_graph_node_id).info("Action Graph Node Rerun start")
            action_graph_result_doc = await ActionGraph.run_node(
                ctx,
                user_actions,
                action_graph_input_dict,
                action_graph_result_doc,
                action_graph_node_id,
                user_action_graph_result,
                webhook
            )
            logger.bind(ctx=ctx, action_graph_node_id=action_graph_node_id).info("Action Graph Node Rerun complete")
        # ACTION GRAPH RESULT - GRAPH RUN / RERUN
        else:
            logger.bind(ctx=ctx).info("Action Graph Run/Rerun Start")
            action_graph_result_doc = await ActionGraph.run_action_graph(
                ctx,
                user_actions,
                user_actions_market,
                action_graph_input_dict,
                action_graph_result_doc,
                user_action_graph_result,
                webhook
            )
            logger.bind(ctx=ctx).info("Action Graph Run/Rerun Complete")

        return action_graph_result_doc

    @staticmethod
    async def run_action_graph(
            ctx: Context,
            user_actions: UserActions,
            user_actions_market: UserActionsMarket,
            action_graph_input_dict: Dict[str, Any],
            action_graph_result_doc: ActionGraphResultDoc,
            user_action_graph_result: UserActionGraphResult,
            webhook: Webhook | None = None
    ) -> ActionGraphResultDoc:
        bind_dict = (LogBinder().with_app_code(AppCode.ACTION_GRAPH_RUN)
                     .with_kwargs(ctx=ctx)
                     .with_action_graph_id(action_graph_result_doc.result.id)
                     .with_action_graph_run_id(action_graph_result_doc.id)
                     .get_bind_dict())
        logger.bind(**bind_dict).info("Action Graph Run Start")
        graph_map = action_graph_result_doc.result.graph
        node_action_map = action_graph_result_doc.result.nodes
        node_details_map = action_graph_result_doc.result.node_details
        action_response: Dict[str, ActionDoc] = action_graph_result_doc.result.output
        # action_graph_input = TextObj.model_validate(action_graph_input_dict)

        total_nodes = await ActionGraph.get_nodes(graph_map)
        inverted_map = await ActionGraph.invert_map(graph_map)

        review_required_nodes: List[str] = []

        count = 0
        try:
            while len(action_response) + len(review_required_nodes) != len(total_nodes):
                count += 1
                if count > 100:
                    logger.bind(**bind_dict).error("Exiting Action Graph Run as total loops > 100")
                    raise StopIteration
                logger.bind(
                    count_action_response=len(action_response),
                    count_review_required_nodes=len(review_required_nodes),
                    count_total_nodes=len(total_nodes),
                    **bind_dict
                ).info("Running Action Graph as action_response + review_required_nodes != total_nodes")
                for node, upstream_nodes in inverted_map.items():
                    if (
                            await ActionGraph.is_work_done([node], action_response) or
                            not await ActionGraph.is_work_done(upstream_nodes, action_response)
                    ):
                        logger.bind(**bind_dict, action_name=node_action_map.get(node)).info(
                            "Continuing to next None as this Node's result is calculated or Upstream dependencies are not met")
                        continue
                    else:
                        logger.bind(**bind_dict, action_name=node_action_map.get(node)).info(
                            "Continuing exec as Node's result not yet calculated and Upstream dependencies are met")
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
                            logger.bind(**bind_dict).info(
                                f"Upstream node requires User review, node_id: {upstream_node}")
                    if is_any_dependent_require_review:
                        (logger
                        .bind(**bind_dict)
                        .info("Continuing to run next node in graph as dependent requires review, node_id: {upstream_node}")
                         )
                        continue
                    else:
                        logger.bind(**bind_dict, action_name=node_action_map.get(node)).info(
                            "Continuing exec as this Node's result is not yet calculated are review requirement are met")

                    if len(upstream_nodes) == 0:
                        # Run action with no dependency
                        action_result: ActionDoc = await ActionGraph.run_action(ctx,
                            user_actions,
                            user_actions_market,
                            node_action_map.get(node),
                            action_graph_input_dict
                        )
                        # action_result = await user_actions.run_action_v1(node_action_map.get(node), action_graph_input.model_dump())

                        action_response[node] = ActionDoc.model_validate(action_result)
                    else:
                        # Run action with at least 1 dependency
                        curr_action = await ActionGraph.get_action(user_actions, user_actions_market,
                                                                   node_action_map.get(node))
                        action_input = await ActionGraph.to_input(ctx, upstream_nodes, curr_action.type,
                                                                  action_response)
                        action_result: ActionDoc = await ActionGraph.run_action(ctx,
                                                                                user_actions,
                                                                                user_actions_market,
                                                                                node_action_map.get(node),
                                                                                action_input.model_dump()
                                                                                )
                        # action_result = await user_actions.run_action_v1(node_action_map.get(node), action_input.model_dump())
                        action_response[node] = ActionDoc.model_validate(action_result)

                        memory_profile = await Profiler.do_memory_profile()
                        logger.bind(ctx=ctx, memory_profile=memory_profile).info(
                            f"Memory profile for Action run {action_result.name}:{action_result.version}")

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
            logger.bind(**bind_dict).info("Exited Action Graph Run While loop len(action_response) + len(review_required_nodes) == len(total_nodes)")

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
        except StopIteration as e:
            logger.bind(**bind_dict).exception(f"Error while graph run, {str(e)}")
        except Exception as e:
            logger.bind(**bind_dict).exception(f"Error while graph run, {str(e)}")

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
        finally:
            logger.bind(**bind_dict).info("Action Graph Run Completed")
            return action_graph_result_doc

    @staticmethod
    async def run_node(
            ctx: Context,
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

        bind_dict = (LogBinder().with_app_code(AppCode.ACTION_GRAPH_RUN)
                     .with_action_graph_id(action_graph_result_doc.result.id)
                     .with_action_graph_run_id(action_graph_result_doc.id)
                     .with_action_id(node_action_doc.id)
                     .get_bind_dict())
        try:
            action_result: ActionDoc = await ActionGraph.run_action_doc(  # noqa F841
                ctx,
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
        except Exception as e:
            logger.bind(ctx=ctx, **bind_dict).info(f"Error in rerun node of Action Graph: {str(e)}")
            return action_graph_result_doc

    @staticmethod
    async def run_action(
            ctx: Context,
            user_actions: UserActions,
            user_action_market: UserActionsMarket,
            action_id: str,
            action_graph_input_dict: Dict[str, Any]
    ) -> ActionDoc:
        logger.bind(ctx=ctx, action_id=action_id).info("Run action")
        exception = None
        try:
            action_result = await user_actions.run_action_v1(ctx, action_id, action_graph_input_dict)
            return action_result
        except HTTPException as e:
            exception = e
        try:
            action_result = await user_action_market.run_market_action(ctx, action_id, action_graph_input_dict)
            return action_result
        except Exception as e:
            raise HTTPException(405, f"{exception.detail} and {e}")

    @staticmethod
    async def get_action(
            user_actions: UserActions,
            user_action_market: UserActionsMarket,
            action_id: str,
    ) -> ActionDoc:
        exception = None
        try:
            action = await user_actions.get_action(action_id)
            if action is None:
                raise HTTPException(404, "Action not found")
            return action
        except HTTPException as e:
            exception = e
        try:
            action = await user_action_market.get_market_action(action_id)
            return action
        except Exception as e:
            raise HTTPException(405, f"{exception.detail} and {e}")

    @staticmethod
    async def run_action_doc(
            ctx: Context,
            user_actions: UserActions,
            action_doc: ActionDoc,
            action_graph_input_dict: Dict[str, Any]
    ) -> ActionDoc:
        try:
            action_doc = await user_actions.run_action_doc(ctx, action_doc, action_graph_input_dict)
            return action_doc
        except Exception as e:
            logger.bind(ctx=ctx).exception(str(e))
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
    async def to_input(
            ctx: Context, upstream_nodes: List[str], current_node_action_type: str, action_response: Dict[str, ActionDoc]
    ) -> MultiObj | Any:
        input_msg = ""

        # curr_action_input = await ActionGraph.gen_input(upstream_nodes, current_node_action_type, action_response)
        # return curr_action_input
        # Use llm to build input obj
        for upstream_node in upstream_nodes:
            upstream_action_doc = action_response.get(upstream_node)
            upstream_action_output_type = ACTION_MAP.get(upstream_action_doc.type).get_output_type()
            if upstream_action_output_type != TextObjs and upstream_action_output_type != TextObj:
                logger.bind(ctx=ctx).info("Choosing llm to generate input for Node")
                curr_action_input = await ActionGraph.gen_input(ctx, upstream_nodes, current_node_action_type,
                                                                action_response)
                logger.bind(ctx=ctx).info("Used llm to generate input for Node")
                return curr_action_input
        # Use manual code to build input obj
        logger.bind(ctx=ctx).info("Choosing manual path to generate input for Node")
        for upstream_node in upstream_nodes:
            action_doc = action_response.get(upstream_node)
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
                            logger.bind(ctx=ctx).info("Added url to input_msg")
                    except Exception:
                        text_obj = TextObj.model_validate(action_output)
                        input_msg = f"{input_msg}\n## {action_doc.name}:\n{text_obj.text}\n\n"
                        logger.bind(ctx=ctx).info("Added TextObj to input_msg")
            except Exception as e:
                logger.bind(ctx=ctx).warning(f"Cannot convert to Input: {str(e)}")
            # if isinstance(action_outputs, TextObjs):
            #     for action_output in action_outputs.texts:
            #         if isinstance(action_output, TextObj):
            #             text_obj = TextObj.model_validate(action_output)
            #             input_msg = f"{input_msg}\n{text_obj.text}"
            # else:
            #     logger.warning("Cannot convert to Input")

        text_obj = MultiObj(text=input_msg)
        return text_obj

    @staticmethod
    async def gen_input(
            ctx: Context, upstream_nodes: List[str], current_node_action_type: str,
            action_response: Dict[str, ActionDoc]
    ) -> Dict[str, Any]:
        try:
            llm_input = ("You are an expert programmer and logician."
                         "Create result json for a given model json schema for result, "
                         "from the input(s) data and its/their json model schema\n\n")
            for upstream_node in upstream_nodes:
                upstream_action_doc = action_response.get(upstream_node)
                upstream_action_output_type = ACTION_MAP.get(upstream_action_doc.type).get_output_type()
                upstream_action_output_model_schema = upstream_action_output_type.model_json_schema()
                upstream_action_output = upstream_action_doc.output
                llm_input += f"#####\nInput model schema:\n{upstream_action_output_model_schema}\n\nInput data:\n{upstream_action_output}\n\n"

            curr_action_input_type = ACTION_MAP.get(current_node_action_type).get_input_type()
            curr_action_input_model_schema = curr_action_input_type.model_json_schema()
            llm_input += f"#####\nOutput model schema:\n{curr_action_input_model_schema}\n\n"
            llm_input += (
                "Add all inputs to give me the output data that adheres to Output model schema. You have to provide only the output in JSON. "
                "Start straight with { and end with }.")

            chat_req = ChatReq(
                model="gpt-4o-mini",
                max_tokens=4096,
                messages=[ChatCompletionUserMessageParam(role="user", content=llm_input)],
                response_format={"type": "json_object"}
            )
            run_input = MultiObj(text=llm_input)
            text_objs: TextObjs = await ActionText2TextLlmChatOpenai(chat_req).run_action(ctx, run_input)
            output_json = text_objs.texts[0].text
            try:
                json_dict = json.loads(output_json)
            except Exception:
                json_dict = output_json
            curr_action_input_obj = curr_action_input_type.model_validate(json_dict)
            logger.bind(ctx=ctx, action_input=curr_action_input_obj).info(
                "Used Llm to generate input by using outputs of upstream nodes")
            return curr_action_input_obj
            # return json_dict
        except Exception as e:
            logger.bind(ctx=ctx).error(f"Cannot generate Input: {str(e)}")
            return {}
