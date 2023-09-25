from abc import abstractmethod
from typing import Any, List

from autobots.action.IAction import IAction
from autobots.conn.openai.image_model import ImageRes
from autobots.prompts.user_prompts import Input


class IActionGenImage(IAction):

    @abstractmethod
    def __init__(self, action_data: Any):
        self.action_data = action_data

    @abstractmethod
    async def run_action(self, action_input: Input) -> List[ImageRes]:
        pass

    @abstractmethod
    async def invoke_action(self, input_str: str) -> List[ImageRes]:
        pass

    @staticmethod
    @abstractmethod
    async def instruction() -> str:
        pass
