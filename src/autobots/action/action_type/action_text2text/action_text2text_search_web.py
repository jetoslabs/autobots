from typing import Type, Literal

from loguru import logger
from pydantic import BaseModel, ValidationError

from src.autobots.action.action.common_action_models import TextObj, TextObjs
from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.duckduckgo.duckduckgo import get_duckduckgo
from src.autobots.conn.duckduckgo.duckduckgo_model import SearchTextParams
from src.autobots.data_model.context import Context
from src.autobots.user.user_orm_model import UserORM


class SearchWebConfig(BaseModel):
    search_type: Literal["web", "news"] = "web"
    search_params: SearchTextParams


class ActionText2TextSearchWeb(ActionABC[SearchWebConfig, SearchWebConfig, SearchWebConfig, TextObj, TextObjs]):
    type = ActionType.text2text_search_web

    @staticmethod
    def get_description() -> str:
        return "Do a duckduckgo search"

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return SearchWebConfig

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return SearchWebConfig

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return SearchWebConfig

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return TextObj

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return TextObjs

    def __init__(self, action_config: SearchWebConfig, user: UserORM | None = None):
        super().__init__(action_config=action_config, user=user)

    async def run_action(self, ctx: Context, action_input: TextObj) -> TextObjs | Exception:
        text_objs = TextObjs(texts=[])
        try:
            duckduckgo = get_duckduckgo()
            self.action_config.search_params.keywords = f"{self.action_config.search_params.keywords} {action_input.text}"
            search_res = []
            match self.action_config.search_type:
                case "news":
                    search_res = await duckduckgo.news(self.action_config.search_params)
                case "web":
                    search_res = await duckduckgo.search_text(self.action_config.search_params)
            for search in search_res:
                # text = f"title: {search.title}\nbody: {search.body}\nhref: {search.href}"
                text = str(search)
                text_objs.texts.append(TextObj(text=text))
            return text_objs
        except ValidationError as e:
            logger.error(str(e))
            return e
        except Exception as e:
            logger.error(str(e))
            return e

    async def run_tool(self, action_config: SearchWebConfig, ctx: Context) -> TextObjs | Exception:
        action = ActionText2TextSearchWeb(action_config)
        action_input = TextObj(text="")
        text_objs = await action.run_action(ctx=ctx, action_input=action_input)
        return text_objs
