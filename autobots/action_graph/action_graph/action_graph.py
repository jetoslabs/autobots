from typing import Dict, List, Set, Any

from fastapi import BackgroundTasks
from pymongo.database import Database

from autobots.action.action.common_action_models import TextObj
from autobots.action.action.user_actions import UserActions
from autobots.action_graph.action_graph.action_graph_doc_model import ActionGraphDoc
from autobots.action_graph.action_graph_result.action_graph_result_model_doc import ActionGraphResultDoc, \
    ActionGraphResultCreate
from autobots.action_graph.action_graph_result.user_action_graph_result import UserActionGraphResult
from autobots.core.log import log
from autobots.event_result.event_result_model import EventResultStatus
from autobots.user.user_orm_model import UserORM


class ActionGraph:

    @staticmethod
    async def run(user: UserORM, input: TextObj, node_action_map: Dict[str, str], graph_map: Dict[str, List[str]],
                  db: Database) -> Dict[str, Any]:
        total_nodes = await ActionGraph.get_nodes(graph_map)
        inverted_map = await ActionGraph.invert_map(graph_map)
        action_response: Dict[str, Any] = {}

        user_actions = UserActions(user, db)
        while len(action_response) != len(total_nodes):
            for node, values in inverted_map.items():
                if await ActionGraph.is_work_done([node], action_response) or \
                        not await ActionGraph.is_work_done(values, action_response):
                    continue
                if len(values) == 0:
                    action_result = await user_actions.run_action(node_action_map.get(node), input.model_dump())
                    action_response[node] = action_result
                else:
                    action_input = await ActionGraph.to_input(values, action_response)
                    action_result = await user_actions.run_action(node_action_map.get(node), action_input.model_dump())
                    action_response[node] = action_result

        return action_response

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
            user_action_graph_result: UserActionGraphResult,
            background_tasks: BackgroundTasks = None
    ) -> ActionGraphResultDoc | None:
        # Create initial Action Graph Result
        action_graph_doc.input = action_graph_input_dict
        action_graph_result_create: ActionGraphResultCreate = ActionGraphResultCreate(
            status=EventResultStatus.processing, result=action_graph_doc, is_saved=False
        )
        action_graph_result_doc = await user_action_graph_result.create_action_graph_result(action_graph_result_create)

        if background_tasks:
            background_tasks.add_task(ActionGraph._run_as_background_task)

        return action_graph_result_doc

    @staticmethod
    async def _run_as_background_task(
            action_graph_input_dict: Dict[str, Any],
            action_graph_result_doc: ActionGraphResultDoc,
            user_action_graph_result: UserActionGraphResult
    ):
        action_graph_result_doc.result.graph


        total_nodes = await ActionGraph.get_nodes(graph_map)
        inverted_map = await ActionGraph.invert_map(graph_map)
        action_response: Dict[str, Any] = {}

        user_actions = UserActions(user, db)
        while len(action_response) != len(total_nodes):
            for node, values in inverted_map.items():
                if await ActionGraph.is_work_done([node], action_response) or \
                        not await ActionGraph.is_work_done(values, action_response):
                    continue
                if len(values) == 0:
                    action_result = await user_actions.run_action(node_action_map.get(node), input.model_dump())
                    action_response[node] = action_result
                else:
                    action_input = await ActionGraph.to_input(values, action_response)
                    action_result = await user_actions.run_action(node_action_map.get(node), action_input.model_dump())
                    action_response[node] = action_result

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
    async def to_input(values: List[str], action_response: Dict[str, Any]) -> TextObj:
        input_msg = ""
        for value in values:
            action_outputs = action_response.get(value)
            if isinstance(action_outputs, list):
                for action_output in action_outputs:
                    if isinstance(action_output, TextObj):
                        text_obj = TextObj.model_validate(action_output)
                        input_msg = f"{input_msg}\n{text_obj.text}"
            else:
                log.warning("Cannot convert to Input")

        text_obj = TextObj(text=input_msg)
        return text_obj
