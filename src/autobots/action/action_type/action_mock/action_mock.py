from typing import Type

from src.autobots.action.action.common_action_models import TextObj
from src.autobots.action.action_type.abc.IAction import IAction, ActionOutputType, ActionInputType, ActionConfigType, \
    ActionConfigUpdateType, ActionConfigCreateType


class MockAction(IAction[TextObj, TextObj, TextObj, TextObj, TextObj]):

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
        return TextObj

    def __init__(self, action_config: TextObj):
        super().__init__(action_config)

    async def run_action(self, action_input: TextObj) -> TextObj:
        output = TextObj(
            text=f"Config_{self.action_config.text}+Input_{action_input.text}+Output"
        )
        return output
