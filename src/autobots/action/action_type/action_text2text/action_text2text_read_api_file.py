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

class ActionText2textAPI(
    ActionABC[None, None, None, None]
):
    type = ActionType.text2text_read_api_file

    @staticmethod
    def get_description() -> str:
        return "Read API definitions from a JSON file"

    @staticmethod
    def get_config_create_type() -> Type[None]:
        return None

    @staticmethod
    def get_config_update_type() -> Type[None]:
        return None

    @staticmethod
    def get_config_type() -> Type[None]:
        return None

    @staticmethod
    def get_input_type() -> Type[None]:
        return None

    @staticmethod
    def get_output_type() -> Type[None]:
        return None

    @staticmethod
    async def update_config(config: None, config_update: None) -> None:
        return None

    def __init__(self, action_config: None, user: UserORM | None = None):
        super().__init__(action_config=action_config, user=user)

    async def get_api_definition(self, key: str, json_file: str) -> None:
        with open(json_file, 'r') as file:
            api_defs = json.load(file)
        return api_defs.get(key)  # Return the specific API definition

    async def run_action(self, ctx: Context, action_input: None) -> None | Exception:
        try:
            config = None
            # Call get_api_definition directly
            api_response = await self.get_api_definition(action_input, "path/to/your/json_file.json")  # Use action_input as key
            return api_response
        except Exception as e:
            logger.error(str(e))
            return e

    async def run_tool(self, action_config: None, ctx: Context) -> None | Exception:
        try:
            config = await ActionText2textAPI.create_config(action_config)
            # Call get_api_definition if needed
            api_response = await self.get_api_definition("some_key", "path/to/your/json_file.json")  # Specify the key
            return api_response
        except Exception as e:
            logger.error(str(e))
            return e