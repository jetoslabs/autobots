from typing import Optional, Type

from pydantic import BaseModel, Field

from src.autobots.action.action.action_doc_model import ActionCreate
from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.useapi.useapi import get_use_api_net
from src.autobots.conn.useapi.text2img.text2img_model import DiscordReqModel, \
    DiscordErrorResponse, DiscordJobsApiResponse
from src.autobots.data_model.context import Context
from src.autobots.user.user_orm_model import UserORM


class Text2ImgRunModel(BaseModel):
    prompt: Optional[str] = Field(default=None,
                                  description="Text prompt with description of the things you want in the image to be generated.")


class ActionCreateText2ImgImagineMidJourney(ActionCreate):
    type: ActionType = ActionType.text2img_imagine_midjourney_ai
    config: DiscordReqModel


class ActionText2ImgMidjourney(
    ActionABC[DiscordReqModel, DiscordReqModel, DiscordReqModel, Text2ImgRunModel, DiscordJobsApiResponse]):
    type = ActionType.text2img_imagine_midjourney_ai

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return DiscordReqModel

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return DiscordReqModel

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return DiscordReqModel

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return Text2ImgRunModel

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return DiscordJobsApiResponse

    def __init__(self, action_config: DiscordReqModel, user: UserORM | None = None):
        super().__init__(action_config=action_config, user=user)

    async def run_action(self, ctx: Context, action_input: Text2ImgRunModel) -> DiscordJobsApiResponse | DiscordErrorResponse:
        if action_input.prompt:
            self.action_config.prompt = f"{self.action_config.prompt}\n{action_input.prompt}"
        res = await get_use_api_net().imagine(self.action_config)
        return res
