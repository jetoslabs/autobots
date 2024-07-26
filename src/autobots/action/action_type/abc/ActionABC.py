from abc import abstractmethod
from typing import TypeVar, Generic, Type, List

from pydantic import BaseModel

from src.autobots.action.action.action_doc_model import ActionResult
from src.autobots.data_model.context import Context
from src.autobots.user.user_orm_model import UserORM

ActionConfigCreateType = TypeVar("ActionConfigCreateType", bound=BaseModel)
ActionConfigUpdateType = TypeVar("ActionConfigUpdateType", bound=BaseModel)
ActionConfigType = TypeVar("ActionConfigType", bound=BaseModel)
ActionInputType = TypeVar("ActionInputType", bound=BaseModel)
ActionOutputType = TypeVar("ActionOutputType", bound=BaseModel)


class ActionABC(
    Generic[
        ActionConfigCreateType, ActionConfigUpdateType, ActionConfigType, ActionInputType, ActionOutputType
    ]
):

    def __init__(self, action_config: ActionConfigType, user: UserORM | None = None, ctx: Context | None = None):
        self.action_config = action_config
        self.user = user
        self.ctx = ctx
        if self.ctx is None:
            self.ctx = Context()

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
    def get_description() -> str:
        return ""
    
    @staticmethod
    async def create_config(config_create: ActionConfigCreateType) -> ActionConfigType | Exception:
        return config_create

    @staticmethod
    async def update_config(config: ActionConfigType, config_update: ActionConfigUpdateType) -> ActionConfigType | Exception:
        return config_update

    @staticmethod
    async def delete_config(config: ActionConfigType) -> ActionConfigType | Exception:
        return config

    @staticmethod
    async def update_config_with_prev_results(
            curr_config: ActionConfigType,
            prev_results: List[ActionResult]
    ) -> ActionConfigType | Exception:
        return curr_config

    @abstractmethod
    async def run_action(self, action_input: ActionInputType) -> ActionOutputType | Exception:
        """To be deprecated in favour of static method run_action"""
        raise NotImplementedError

    @abstractmethod
    async def run_tool(self, action_config: ActionConfigType) -> ActionOutputType | Exception:
        """DO NOT change the signature of the function. It is used to generate function definition for LLMs"""
        raise NotImplementedError
