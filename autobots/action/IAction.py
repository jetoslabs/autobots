from abc import abstractmethod
from typing import Protocol, Any


class IAction(Protocol):
    @abstractmethod
    def __init__(self, action_data: Any):
        self.action_data = action_data

    @abstractmethod
    async def run_action(self, action_input: Any) -> Any:
        pass

    @abstractmethod
    async def invoke_action(self, input_str: str) -> Any:
        pass

    @staticmethod
    @abstractmethod
    async def instruction() -> str:
        pass
