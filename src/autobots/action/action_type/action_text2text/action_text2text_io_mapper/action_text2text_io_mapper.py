from typing import Dict, Any, Type

from pydantic import BaseModel

from src.autobots.action.action.common_action_models import TextObjs
from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_text2text.action_text2text_io_mapper.io_mapper import IOMapperConfig, IOMapper
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.data_model.context import Context
from src.autobots.user.user_orm_model import UserORM


class IOMapperInput(BaseModel):
    input_action_output: Dict[str, Any]
    input_action_type: ActionType | None = None


class ActionText2TextIOMapper(ActionABC[IOMapperConfig, IOMapperConfig, IOMapperConfig, IOMapperInput, TextObjs]):
    type = ActionType.text2text_io_mapper

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return IOMapperConfig

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return IOMapperConfig

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return IOMapperConfig

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return IOMapperInput

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return TextObjs

    def __init__(self, action_config: IOMapperConfig, user: UserORM | None = None):
        super().__init__(action_config=action_config, user=user)

    async def run_action(self, ctx: Context, action_input: IOMapperInput) -> TextObjs | None:
        if action_input.input_action_output:
            self.action_config.prev_action_output = action_input.input_action_output
        if action_input.input_action_type:
            self.action_config.prev_action_type = action_input.input_action_type
        resp = await IOMapper().map_to_output(self.action_config)
        return resp
