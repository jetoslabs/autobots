from typing import Type

from pydantic import BaseModel, ValidationError, HttpUrl

from autobots.action.action.common_action_models import TextObj, TextObjs
from autobots.action.action_type.abc.IAction import IAction, ActionConfigType, ActionInputType, ActionOutputType
from autobots.action.action_type.action_types import ActionType
from autobots.conn.selenium.selenium import get_selenium
from autobots.core.logging.log import Log


class ReadUrlConfig(BaseModel):
    xpath: str = "/html/body"
    attribute: str = ""


class ActionText2TextReadUrl(IAction[ReadUrlConfig, TextObj, TextObjs]):
    type = ActionType.text2text_read_url

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return ReadUrlConfig

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return TextObj

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return TextObjs

    def __init__(self, action_config: ReadUrlConfig):
        super().__init__(action_config)

    async def run_action(self, action_input: TextObj) -> TextObjs:
        text_objs = TextObjs(texts=[])
        try:
            selenium = get_selenium()
            out = await selenium.read_url_v1(
                HttpUrl(action_input.text),
                self.action_config.xpath,
                self.action_config.attribute
            )
            text_objs.texts.append(TextObj(text=out))
            return text_objs
        except ValidationError as e:
            Log.error(str(e))
        except Exception as e:
            Log.error(str(e))

