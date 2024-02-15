from abc import abstractmethod
from typing import TypeVar, Generic, Type

from pydantic import BaseModel

ActionConfigType = TypeVar("ActionConfigType", bound=BaseModel)
ActionInputType = TypeVar("ActionInputType", bound=BaseModel)
ActionOutputType = TypeVar("ActionOutputType", bound=BaseModel)


class IAction(Generic[ActionConfigType, ActionInputType, ActionOutputType]):
    def __init__(self, action_config: ActionConfigType):
        self.action_config = action_config

    @staticmethod
    @abstractmethod
    def get_config_type() -> Type[ActionConfigType]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_input_type() -> Type[ActionInputType]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_output_type() -> Type[ActionOutputType]:
        raise NotImplementedError

    @abstractmethod
    async def run_action(self, action_input: ActionInputType) -> ActionOutputType:
        raise NotImplementedError
