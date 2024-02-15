from typing import Optional, Type

from pydantic import BaseModel, Field

from src.autobots.action.action.action_doc_model import ActionCreate
from src.autobots.action.action_type.abc.IAction import (
    IAction,
    ActionOutputType,
    ActionInputType,
    ActionConfigType,
)
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.stable_diffusion.common_models import StableDiffusionRes
from src.autobots.conn.stable_diffusion.stable_diffusion import get_stable_diffusion
from src.autobots.conn.stable_diffusion.text2video.text2video_model import (
    Text2VideoReqModel,
    Text2VideoScheduler,
)


class Text2VideoRunModel(BaseModel):
    prompt: Optional[str] = Field(
        None,
        description="Text prompt with description of the things you want in the video to be generated.",
    )
    negative_prompt: Optional[str] = Field(
        default=None, description="Items you don't want in the video."
    )
    scheduler: Optional[Text2VideoScheduler] = Field(
        default=Text2VideoScheduler.UniPCMultistepScheduler.value,
        description="Use it to set a scheduler for video creation.",
    )
    seconds: Optional[int] = Field(
        default=3, description="Duration of the video in seconds."
    )


class ActionCreateText2VideoStableDiffusion(ActionCreate):
    type: ActionType = ActionType.text2video_stable_diffusion
    config: Text2VideoReqModel
    input: Optional[Text2VideoRunModel] = None
    output: Optional[StableDiffusionRes] = None


class ActionText2VideoStableDiffusion(
    IAction[Text2VideoReqModel, Text2VideoRunModel, StableDiffusionRes]
):
    type = ActionType.text2video_stable_diffusion

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return Text2VideoReqModel

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return Text2VideoRunModel

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return StableDiffusionRes

    def __init__(self, action_config: Text2VideoReqModel):
        super().__init__(action_config)

    async def run_action(self, action_input: Text2VideoRunModel) -> StableDiffusionRes:
        if action_input.prompt:
            self.action_config.prompt = (
                f"{self.action_config.prompt}\n{action_input.prompt}"
            )
        if action_input.negative_prompt:
            self.action_config.negative_prompt = (
                f"{self.action_config.negative_prompt}\n{action_input.negative_prompt}"
            )
        if action_input.scheduler:
            self.action_config.scheduler = action_input.scheduler
        if action_input.seconds:
            self.action_config.seconds = action_input.seconds
        video = await get_stable_diffusion().text2video(self.action_config)
        return video
