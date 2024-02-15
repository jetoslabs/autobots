from typing import Type

from loguru import logger
from pydantic import BaseModel, ValidationError, HttpUrl

from src.autobots.action.action.common_action_models import TextObj, TextObjs
from src.autobots.action.action_type.abc.IAction import (
    IAction,
    ActionConfigType,
    ActionInputType,
    ActionOutputType,
)
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.selenium.selenium import get_selenium


class ReadUrlConfig(BaseModel):
    xpath: str = "/html/body"
    attribute: str = ""


class ActionText2TextReadUrl(
    IAction[ReadUrlConfig, TextObj, TextObjs]
):  # TODO: add `s` at the end
    type = ActionType.text2text_read_url  # TODO: add `s` at the end

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
            urls = []
            potential_urls = action_input.text.split(",")
            for potential_url in potential_urls:
                try:
                    urls.append(HttpUrl(potential_url))
                except Exception as e:
                    pass

            out = await selenium.read_urls(
                urls, self.action_config.xpath, self.action_config.attribute
            )

            # out = await selenium.read_url_v1(
            #     HttpUrl(action_input.text),
            #     self.action_config.xpath,
            #     self.action_config.attribute
            # )
            text_objs.texts.append(TextObj(text=out))
            return text_objs
        except ValidationError as e:
            logger.error(str(e))
        except Exception as e:
            logger.error(str(e))
