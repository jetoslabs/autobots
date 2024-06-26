from typing import Type

from loguru import logger
from pydantic import BaseModel, ValidationError, HttpUrl

from src.autobots.action.action.common_action_models import TextObj, TextObjs
from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.selenium.selenium import get_selenium


class ReadUrlConfig(BaseModel):
    xpath: str = "/html/body"
    attribute: str = ""


class ActionText2TextReadUrl(ActionABC[ReadUrlConfig, ReadUrlConfig, ReadUrlConfig, TextObj, TextObjs]):#TODO: add `s` at the end
    type = ActionType.text2text_read_url #TODO: add `s` at the end

    @staticmethod
    def get_description() -> str:
        return "Scrape data from a URL"

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return ReadUrlConfig

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return ReadUrlConfig

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
                except Exception:
                    pass

            out = await selenium.read_urls(urls, self.action_config.xpath, self.action_config.attribute)

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

    @staticmethod
    async def create_and_run_action(action_config: ReadUrlConfig) -> TextObjs:
        action = ActionText2TextReadUrl(action_config)
        action_input = TextObj(text="")
        return await action.run_action(action_input)
