from abc import abstractmethod
from typing import Protocol, TypeVar

from pydantic import BaseModel

ActionConfigType = TypeVar("ActionConfigType", bound=BaseModel)
ActionInputType = TypeVar("ActionInputType", bound=BaseModel)
ActionOutputType = TypeVar("ActionOutputType", bound=BaseModel)


class IAction(Protocol[ActionConfigType, ActionInputType, ActionOutputType]):
    @abstractmethod
    def __init__(self, action_config: ActionConfigType):
        self.action_data = action_config

    @abstractmethod
    async def run_action(self, action_input: ActionInputType) -> ActionOutputType:
        raise NotImplementedError

    # @abstractmethod
    # async def invoke_action(self, input_str: str) -> ActionOutputSchemaType:
    #     raise NotImplementedError
    #
    # @staticmethod
    # @abstractmethod
    # async def instruction() -> str:
    #     pass
