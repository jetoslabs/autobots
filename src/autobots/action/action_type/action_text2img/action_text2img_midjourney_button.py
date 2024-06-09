from typing import Optional, Type

from pydantic import BaseModel, Field

from src.autobots.action.action.action_doc_model import ActionCreate
from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.useapi.useapi import get_use_api_net
from src.autobots.conn.useapi.text2img.text2img_model import DiscordReqModel, \
    DiscordErrorResponse, DiscordJobsApiResponse


class Text2ImgRunModelButton(BaseModel):
    button: Optional[str] = Field(default=None,
                                  description="button you want to run on a generated image")
    job_id: Optional[str] = Field(default=None,
                                  description="job id of a processed image via midjourney")


class ActionCreateText2ImgButtonMidJourney(ActionCreate):
    type: ActionType = ActionType.text2img_button_midjourney_ai
    config: DiscordReqModel


class ActionText2ImgMidjourneyButton(
    ActionABC[DiscordReqModel, DiscordReqModel, DiscordReqModel, Text2ImgRunModelButton, DiscordJobsApiResponse]):
    type = ActionType.text2img_button_midjourney_ai

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
        return Text2ImgRunModelButton

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return DiscordJobsApiResponse

    def __init__(self, action_config: DiscordReqModel):
        super().__init__(action_config)

    async def run_action(self, action_input: Text2ImgRunModelButton) -> DiscordJobsApiResponse | DiscordErrorResponse:
        if action_input.button:
            self.action_config.button = f"{self.action_config.button}{action_input.button}"
        if action_input.job_id:
            self.action_config.job_id = f"{self.action_config.job_id}{action_input.job_id}"
        res = await get_use_api_net().button(self.action_config)
        return res
