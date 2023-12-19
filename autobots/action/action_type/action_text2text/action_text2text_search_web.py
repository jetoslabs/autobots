from typing import Type

from pydantic import BaseModel, ValidationError

from autobots.action.action.common_action_models import TextObj, TextObjs
from autobots.action.action_type.abc.IAction import IAction, ActionConfigType, ActionInputType, ActionOutputType
from autobots.action.action_type.action_types import ActionType
from autobots.conn.duckduckgo.duckduckgo import get_duckduckgo
from autobots.core.logging.log import Log


class SearchWebConfig(BaseModel):
    text: str = ""
    num_results: int = 3


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
            browse_input = f"{self.action_config.text} {action_input.text}"
            search_res = await duckduckgo.search_text(browse_input, self.action_config.num_results)
            for search in search_res:
                text_objs.texts.append(TextObj(text=search.model_dump_json()))
            return text_objs
        except ValidationError as e:
            Log.error(str(e))
        except Exception as e:
            Log.error(str(e))
