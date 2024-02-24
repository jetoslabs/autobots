from typing import Optional, Type

from pydantic import BaseModel, Field

from src.autobots.action.action.action_doc_model import ActionCreate
from src.autobots.action.action_type.abc.IAction import IAction, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.useapi.useapi import get_use_api_net
from src.autobots.conn.useapi.text2img.text2img_model import DiscordJobReqModel, DiscordReqModel, \
    DiscordJobsApiResponse, DiscordImagineApiResponse, DiscordErrorResponse


class Text2ImgJobRunModel(BaseModel):
    job_id: Optional[str] = Field(default=None,
                                  description="Mid Journey job id")


class ActionCreateText2ImgMidJourneyJob(ActionCreate):
    type: ActionType = ActionType.text2img_midjourney_ai
    config: DiscordReqModel


class ActionText2ImgMidjourneyJob(IAction[DiscordReqModel, DiscordReqModel, DiscordReqModel, Text2ImgJobRunModel, DiscordImagineApiResponse]):
    type = ActionType.text2img_midjourney_ai

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
        return Text2ImgJobRunModel

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return DiscordJobsApiResponse

    def __init__(self, action_config: DiscordJobReqModel):
        super().__init__(action_config)


    async def run_action(self, action_input: Text2ImgJobRunModel) -> DiscordJobsApiResponse | DiscordErrorResponse:
        if action_input.job_id: self.action_config.job_id = f"{self.action_config.job_id}\n{action_input.job_id}"
        res = await get_use_api_net().jobs(self.action_config)
        return res