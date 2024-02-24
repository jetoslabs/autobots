from typing import Type

from src.autobots.action.action.common_action_models import TextObj, TextObjs
from src.autobots.action.action_type.abc.IAction import IAction, ActionInputType, ActionOutputType, ActionConfigType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType


class ActionText2textUserInput(IAction[TextObj, TextObj, TextObj, TextObj, TextObjs]):
    type = ActionType.text2text_user_input

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

    async def run_action(self, action_input: TextObj) -> TextObjs:
        text_objs = TextObjs(texts=[])
        if self.action_config.text:
            text_objs.texts.append(self.action_config)
        if action_input.text:
            text_objs.texts.append(action_input)
        return text_objs
