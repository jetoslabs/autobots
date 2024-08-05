import json
import typing
from typing import Type, Dict

import httpx
from httpx._types import PrimitiveData
from loguru import logger
from pydantic import BaseModel, ConfigDict, HttpUrl

from src.autobots.action.action_type.abc.ActionABC import ActionABC
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.data_model.context import Context
from src.autobots.user.user_orm_model import UserORM

class ActionConfig(BaseModel):
    key: str

class ActionInput(BaseModel):
    key: str

class ActionOutput(BaseModel):  # Define ActionOutput as a Pydantic model
    text: str

class ActionText2textReadApiFile(
    ActionABC[ActionConfig, ActionConfig, ActionConfig, ActionInput, ActionOutput]
):
    type = ActionType.text2text_read_api_file

    @staticmethod
    def get_description() -> str:
        return "Read API definitions from a JSON file"

    @staticmethod
    def get_config_create_type() -> Type[ActionConfig]:
        return ActionConfig

    @staticmethod
    def get_config_update_type() -> Type[ActionConfig]:
        return ActionConfig

    @staticmethod
    def get_config_type() -> Type[ActionConfig]:
        return ActionConfig

    @staticmethod
    def get_input_type() -> Type[ActionInput]:
        return ActionInput

    @staticmethod
    def get_output_type() -> Type[ActionOutput]:
        return ActionOutput

    @staticmethod
    async def update_config(config: ActionConfig, config_update: ActionConfig) -> None:
        return None

    def __init__(self, action_config: ActionConfig, user: UserORM | None = None):
        super().__init__(action_config=action_config, user=user)

    async def get_api_definition(self, key: str, json_file: str) -> None:
        with open(json_file, 'r') as file:
            api_defs = json.load(file)
        return api_defs.get(key)  # Return the specific API definition

    async def run_action(self, ctx: Context, action_input: ActionInput) -> ActionOutput | Exception:
        try:
            api_response = await self.get_api_definition(action_input.key, "path/to/your/json_file.json")  # Use action_input.key as key
            return ActionOutput(text=json.dumps(api_response))  # Convert dict to JSON string
        except Exception as e:
            logger.error(str(e))
            return e

    async def run_tool(self, action_config: ActionConfig, ctx: Context) -> ActionOutput | Exception:
        try:
            api_response = await self.get_api_definition(action_config.key, "path/to/your/json_file.json")  # Specify the key
            return ActionOutput(text=json.dumps(api_response))  # Convert dict to JSON string
        except Exception as e:
            logger.error(str(e))
            return e