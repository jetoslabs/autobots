from typing import Literal, Type

from loguru import logger
from pydantic import BaseModel, ValidationError

from src.autobots.action.action.common_action_models import TextObj, TextObjs
from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.duckduckgo.duckduckgo import get_duckduckgo
from src.autobots.conn.duckduckgo.duckduckgo_model import SearchMapsParams
from src.autobots.data_model.context import Context
from src.autobots.user.user_orm_model import UserORM


class SearchMapsConfig(BaseModel):
    search_type: Literal["maps"] = "maps"
    search_params: SearchMapsParams


class ActionText2TextSearchMaps(ActionABC[SearchMapsConfig, SearchMapsConfig, SearchMapsConfig, TextObj, TextObjs]):
    type = ActionType.text2text_search_maps

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return SearchMapsConfig

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return SearchMapsConfig

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return SearchMapsConfig

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return TextObj

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return TextObjs

    def __init__(self, action_config: TextObj, user: UserORM | None = None):
        super().__init__(action_config=action_config, user=user)

    async def run_action(self, ctx: Context, action_input: TextObj) -> TextObjs:
        text_objs = TextObjs(texts=[])
        try:
            duckduckgo = get_duckduckgo()
            self.action_config.search_params.keywords = f"{self.action_config.search_params.keywords} {action_input.text}"
            search_res = await duckduckgo.search_maps(self.action_config.search_params)
            for search in search_res:
                # text = f"title: {search.title}\nbody: {search.body}\nhref: {search.href}"
                text = str(search)
                text_objs.texts.append(TextObj(text=text))
            return text_objs
        except ValidationError as e:
            logger.error(str(e))
        except Exception as e:
            logger.error(str(e))
