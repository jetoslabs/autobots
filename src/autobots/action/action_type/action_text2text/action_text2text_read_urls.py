from typing import Type

from loguru import logger
from pydantic import BaseModel, ValidationError, HttpUrl

from src.autobots.action.action.common_action_models import TextObj, TextObjs
from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.selenium.selenium import get_selenium
from src.autobots.data_model.context import Context
from src.autobots.user.user_orm_model import UserORM


class ReadUrlConfig(BaseModel):
    url: HttpUrl | None = None
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

    def __init__(self, action_config: ReadUrlConfig, user: UserORM | None = None):
        super().__init__(action_config=action_config, user=user)

    async def run_action(self, ctx: Context, action_input: TextObj) -> TextObjs:
        text_objs = TextObjs(texts=[])
        try:
            selenium = get_selenium()
            urls = []
            potential_urls = action_input.text.split(",")
            potential_urls.append(self.action_config.url) if self.action_config.url else None
            for potential_url in potential_urls:
                try:
                    urls.append(HttpUrl(potential_url))
                except Exception as e:
                    logger.error(str(e))
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

    async def run_tool(self, action_config: ReadUrlConfig, ctx: Context) -> TextObjs | Exception:
        text_objs = TextObjs(texts=[])
        try:
            selenium = get_selenium()
            urls = []
            potential_urls = [action_config.url]
            for potential_url in potential_urls:
                try:
                    urls.append(HttpUrl(potential_url))
                except Exception as e:
                    logger.error(str(e))
                    pass

            out = await selenium.read_urls(urls, action_config.xpath, action_config.attribute)
            text_objs.texts.append(TextObj(text=out))
            return text_objs
        except ValidationError as e:
            logger.error(str(e))
            return e
        except Exception as e:
            logger.error(str(e))
            return e
