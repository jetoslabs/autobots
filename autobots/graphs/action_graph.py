from typing import Dict, List, Set, Any

from pymongo.database import Database

from autobots.action.user_actions import UserActions
from autobots.conn.openai.chat import Message
from autobots.core.log import log
from autobots.prompts.user_prompts import Input
from autobots.user.user_orm_model import UserORM


class ActionGraph:

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
    async def run(user: UserORM, input: Input, graph_map: Dict[str, List[str]], db: Database) -> Dict[str, Any]:
        total_nodes = await ActionGraph.get_nodes(graph_map)
        inverted_map = await ActionGraph.invert_map(graph_map)
        action_response: Dict[str, Any] = {}

        user_actions = UserActions(user)
        while len(action_response) != len(total_nodes):
            for node, values in inverted_map.items():
                if await ActionGraph.is_work_done([node], action_response) or \
                        not await ActionGraph.is_work_done(values, action_response):
                    continue
                if len(values) == 0:
                    action_result = await user_actions.run_action(node, input, db)
                    action_response[node] = action_result
                else:
                    action_input = await ActionGraph.to_input(values, action_response)
                    action_result = await user_actions.run_action(node, action_input, db)
                    action_response[node] = action_result

        return action_response

    @staticmethod
    async def is_work_done(values: List[str], action_response: Dict[str, Any]) -> bool:
        for value in values:
            if value not in action_response:
                return False
        return True

    @staticmethod
    async def to_input(values: List[str], action_response: Dict[str, Any]) -> Input:
        input_msg = ""
        for value in values:
            action_output = action_response.get(value)
            if isinstance(action_output, Message):
                message = Message.model_validate(action_output)
                input_msg = input_msg + message.content
            else:
                log.warning("Cannot convert to Input")

        return Input(input=input_msg)
