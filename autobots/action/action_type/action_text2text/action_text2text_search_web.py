from typing import Type, Literal

from pydantic import BaseModel, ValidationError

from autobots.action.action.common_action_models import TextObj, TextObjs
from autobots.action.action_type.abc.IAction import IAction, ActionConfigType, ActionInputType, ActionOutputType
from autobots.action.action_type.action_types import ActionType
from autobots.conn.duckduckgo.duckduckgo import get_duckduckgo
from autobots.conn.duckduckgo.duckduckgo_model import SearchTextParams
from autobots.core.logging.log import Log


class SearchWebConfig(BaseModel):
    search_type: Literal["web", "news"] = "web"
    search_params: SearchTextParams


class ActionText2TextSearchWeb(IAction[SearchWebConfig, TextObj, TextObjs]):
    type = ActionType.text2text_search_web

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return SearchWebConfig

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return TextObj

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return TextObjs

    def __init__(self, action_config: TextObj):
        super().__init__(action_config)

    async def run_action(self, action_input: TextObj) -> TextObjs:
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
            Log.error(str(e))
        except Exception as e:
            Log.error(str(e))
