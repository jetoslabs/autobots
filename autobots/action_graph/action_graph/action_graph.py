from typing import Dict, List, Set, Any

from fastapi import BackgroundTasks

from autobots.action.action.action_doc_model import ActionDoc
from autobots.action.action.common_action_models import TextObj, TextObjs
from autobots.action.action.user_actions import UserActions
from autobots.action_graph.action_graph.action_graph_doc_model import ActionGraphDoc
from autobots.action_graph.action_graph_result.action_graph_result_model_doc import ActionGraphResultDoc, \
    ActionGraphResultCreate, ActionGraphResultUpdate
from autobots.action_graph.action_graph_result.user_action_graph_result import UserActionGraphResult
from autobots.core.log import log
from autobots.event_result.event_result_model import EventResultStatus


class ActionGraph:

    # @staticmethod
    # async def run(user: UserORM, input: TextObj, node_action_map: Dict[str, str], graph_map: Dict[str, List[str]],
    #               db: Database) -> Dict[str, Any]:
    #     total_nodes = await ActionGraph.get_nodes(graph_map)
    #     inverted_map = await ActionGraph.invert_map(graph_map)
    #     action_response: Dict[str, Any] = {}
    #
    #     user_actions = UserActions(user, db)
    #     while len(action_response) != len(total_nodes):
    #         for node, values in inverted_map.items():
    #             if await ActionGraph.is_work_done([node], action_response) or \
    #                     not await ActionGraph.is_work_done(values, action_response):
    #                 continue
    #             if len(values) == 0:
    #                 action_result = await user_actions.run_action(node_action_map.get(node), input.model_dump())
    #                 action_response[node] = action_result
    #             else:
    #                 action_input = await ActionGraph.to_input(values, action_response)
    #                 action_result = await user_actions.run_action(node_action_map.get(node), action_input.model_dump())
    #                 action_response[node] = action_result
    #
    #     return action_response

    @staticmethod
    async def run_in_background(
            # user: UserORM,
            # input: TextObj,
            # node_action_map: Dict[str, str],
            # graph_map: Dict[str, List[str]],
            # db: Database,
            # user_action_graph_result: UserActionGraphResult,
            # background_tasks: BackgroundTasks,
            action_graph_doc: ActionGraphDoc,
            action_graph_input_dict: Dict[str, Any],
            user_actions: UserActions,
            user_action_graph_result: UserActionGraphResult,
            background_tasks: BackgroundTasks = None
    ) -> ActionGraphResultDoc | None:
        # Create initial Action Graph Result
        action_graph_doc.input = action_graph_input_dict
        action_graph_doc.output = {}
        action_graph_result_create: ActionGraphResultCreate = ActionGraphResultCreate(
            status=EventResultStatus.processing, result=action_graph_doc, is_saved=False
        )
        action_graph_result_doc = await user_action_graph_result.create_action_graph_result(action_graph_result_create)

        if background_tasks:
            background_tasks.add_task(
                ActionGraph._run_as_background_task,
                user_actions,
                action_graph_input_dict,
                action_graph_result_doc,
                user_action_graph_result
            )
        else:
            action_graph_result_doc = await ActionGraph._run_as_background_task(
                user_actions,
                action_graph_input_dict,
                action_graph_result_doc,
                user_action_graph_result
            )

        return action_graph_result_doc

    @staticmethod
    async def _run_as_background_task(
            user_actions: UserActions,
            action_graph_input_dict: Dict[str, Any],
            action_graph_result_doc: ActionGraphResultDoc,
            user_action_graph_result: UserActionGraphResult
    ):
        graph_map = action_graph_result_doc.result.graph
        node_action_map = action_graph_result_doc.result.nodes
        action_graph_input = TextObj.model_validate(action_graph_input_dict)

        total_nodes = await ActionGraph.get_nodes(graph_map)
        inverted_map = await ActionGraph.invert_map(graph_map)
        action_response: Dict[str, ActionDoc] = {}

        try:
            while len(action_response) != len(total_nodes):
                for node, values in inverted_map.items():
                    if await ActionGraph.is_work_done([node], action_response) or \
                            not await ActionGraph.is_work_done(values, action_response):
                        continue
                    if len(values) == 0:
                        action_result = await user_actions.run_action_v1(node_action_map.get(node), action_graph_input.model_dump())
                        action_response[node] = ActionDoc.model_validate(action_result)
                    else:
                        action_input = await ActionGraph.to_input(values, action_response)
                        action_result = await user_actions.run_action_v1(node_action_map.get(node), action_input.model_dump())
                        action_response[node] = ActionDoc.model_validate(action_result)

                    # Update action result graph
                    action_graph_result_doc.result.output[node] = action_response[node]
                    action_graph_result_update: ActionGraphResultUpdate = ActionGraphResultUpdate(
                        result=action_graph_result_doc.result
                    )
                    action_graph_result_doc = await user_action_graph_result.update_action_graph_result(
                        action_graph_result_doc.id,
                        action_graph_result_update
                    )

            # Update action result graph as success
            action_graph_result_update: ActionGraphResultUpdate = ActionGraphResultUpdate(
                status=EventResultStatus.success
            )
            action_graph_result_doc = await user_action_graph_result.update_action_graph_result(
                action_graph_result_doc.id,
                action_graph_result_update
            )
        except Exception as e:
            log.error("Error while graph run")
            # Update action result graph as error
            action_graph_result_update: ActionGraphResultUpdate = ActionGraphResultUpdate(
                status=EventResultStatus.error
            )
            action_graph_result_doc = await user_action_graph_result.update_action_graph_result(
                action_graph_result_doc.id,
                action_graph_result_update
            )
        log.info("Completed Action Graph _run_as_background_task")
        return action_graph_result_doc


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
            if isinstance(action_outputs, TextObjs):
                for action_output in action_outputs.texts:
                    if isinstance(action_output, TextObj):
                        text_obj = TextObj.model_validate(action_output)
                        input_msg = f"{input_msg}\n{text_obj.text}"
            else:
                log.warning("Cannot convert to Input")

        text_obj = TextObj(text=input_msg)
        return text_obj
