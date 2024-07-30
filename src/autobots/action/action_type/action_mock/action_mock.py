from typing import Type

from src.autobots.action.action.common_action_models import TextObj, TextObjs
from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionOutputType, ActionInputType, ActionConfigType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.data_model.context import Context
from src.autobots.user.user_orm_model import UserORM


class MockAction(ActionABC[TextObj, TextObj, TextObj, TextObj, TextObjs]):

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return TextObj

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return TextObj

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return TextObj

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return TextObj

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return TextObjs

    def __init__(self, action_config: TextObj, user: UserORM | None = None):
        super().__init__(action_config=action_config, user=user)

    async def run_action(self, ctx: Context, action_input: TextObj) -> TextObjs:
        text_obj = TextObj(
            text=f"Config_{self.action_config.text}+Input_{action_input.text}+Output"
        )
        output = TextObjs(texts=[text_obj])
        return output
