from abc import abstractmethod
from typing import TypeVar, Generic, Type

from pydantic import BaseModel

ActionConfigCreateType = TypeVar("ActionConfigCreateType", bound=BaseModel)
ActionConfigUpdateType = TypeVar("ActionConfigUpdateType", bound=BaseModel)
ActionConfigType = TypeVar("ActionConfigType", bound=BaseModel)
ActionInputType = TypeVar("ActionInputType", bound=BaseModel)
ActionOutputType = TypeVar("ActionOutputType", bound=BaseModel)


class IAction(
    Generic[ActionConfigCreateType, ActionConfigUpdateType, ActionConfigType, ActionInputType, ActionOutputType]):

    def __init__(self, action_config: ActionConfigType):
        self.action_config = action_config

    @staticmethod
    @abstractmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        raise NotImplementedError

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

    @staticmethod
    async def create_config(config_create: ActionConfigCreateType) -> ActionConfigType:
        return config_create

    @staticmethod
    async def update_config(config: ActionConfigType, config_update: ActionConfigUpdateType) -> ActionConfigType:
        return config_update

    @staticmethod
    async def delete_config(config: ActionConfigType) -> ActionConfigType:
        return config

    @staticmethod
    async def update_config_with_prev_IO(
            curr_config: ActionConfigType,
            prev_input: ActionInputType | None = None,
            prev_output: ActionOutputType | None = None,
    ) -> ActionConfigType:
        return curr_config

    @abstractmethod
    async def run_action(self, action_input: ActionInputType) -> ActionOutputType:
        raise NotImplementedError
