from abc import abstractmethod
from typing import Any

from autobots.action.IAction import IAction
from autobots.conn.openai.chat import Message
from autobots.prompts.user_prompts import Input


class IActionGenText(IAction):

    @abstractmethod
    def __init__(self, action_data: Any):
        self.action_data = action_data

    @abstractmethod
    async def run_action(self, action_input: Input) -> Message:
        pass

    @abstractmethod
    async def invoke_action(self, input_str: str) -> Message:
        pass

    @staticmethod
    @abstractmethod
    async def instruction() -> str:
        pass
