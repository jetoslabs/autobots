from typing import Type

from src.autobots.action.action.common_action_models import TextObj, TextObjs
from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionOutputType, ActionInputType, ActionConfigType, \
    ActionConfigUpdateType, ActionConfigCreateType


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

    def __init__(self, action_config: TextObj):
        super().__init__(action_config)

    async def run_action(self, action_input: TextObj) -> TextObjs:
        text_obj = TextObj(
            text=f"Config_{self.action_config.text}+Input_{action_input.text}+Output"
        )
        output = TextObjs(texts=[text_obj])
        return output
