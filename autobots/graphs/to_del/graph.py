import uuid
from typing import Dict, List, Set

from sqlalchemy.orm import Session

from autobots.core.log import log
from autobots.prompts.prompt_orm_model import PromptORM
from autobots.prompts.user_prompts import UserPrompts, TextObj
from autobots.user.user_orm_model import UserORM


class Graph:

    @staticmethod
    async def collect_nodes(graph: Dict[str, List[str]]) -> Set[str]:
        nodes: Set[str] = set()
        for key, values in graph.items():
            nodes.add(key)
            for val in values:
                nodes.add(val)
        return nodes

    @staticmethod
    async def prompts_for_user(user: UserORM, graph: Dict[str, List[str]], db: Session) -> Dict[str, PromptORM]:
        node_prompt_map: Dict[str, PromptORM] = {}
        nodes = await Graph.collect_nodes(graph)
        user_prompts = UserPrompts(user)
        for node in nodes:
            try:
                user_prompt = await user_prompts.read(uuid.UUID(node), db)
                node_prompt_map[node] = user_prompt
            except Exception as e:
                log.error(f"Prompt: {node} not found for user: {user.id}")
        return node_prompt_map

    @staticmethod
    async def invert_map(graph: Dict[str, List[str]]) -> Dict[str, List[str]]:
        inverted_map: Dict[str, List[str]] = {}

        nodes = await Graph.collect_nodes(graph)
        for node in nodes:
            inverted_map[node] = []

        for key, values in graph.items():
            for value in values:
                inverted_map[value] = inverted_map.get(value) + [key]

        return inverted_map

    @staticmethod
    async def run(user: UserORM, input: TextObj, graph_map: Dict[str, List[str]], db: Session) -> Dict[str, str]:
        user_prompts = UserPrompts(user)
        prompts = await Graph.prompts_for_user(user, graph_map, db)
        inverted_map = await Graph.invert_map(graph_map)
        prompt_response: Dict[str, str] = {}

        while len(prompt_response) != len(prompts):
            for node, values in inverted_map.items():
                if await Graph.is_work_done([node], prompt_response) or not await Graph.is_work_done(values, prompt_response):
                    continue
                if len(values) == 0:
                    message = await user_prompts.run(uuid.UUID(node), input, db)
                    prompt_response[node] = message.content
                else:
                    input_msg = ""
                    for value in values:
                        input_msg = input_msg + prompt_response.get(value)
                    message = await user_prompts.run(uuid.UUID(node), TextObj(input=input_msg), db)
                    prompt_response[node] = message.content

        return prompt_response

    @staticmethod
    async def is_work_done(values: List[str], prompt_response: Dict[str, str]) -> bool:
        for value in values:
            if value not in prompt_response:
                return False
        return True
