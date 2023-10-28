from typing import Optional

from pydantic import BaseModel, Field

from autobots.action.action.action_doc_model import ActionCreate
from autobots.action.action_type.abc.IAction import IAction
from autobots.action.action_type.abc.IActionGenImage import IActionGenImage
from autobots.action.action_type.action_types import ActionType
from autobots.conn.stable_diffusion.common_models import StableDiffusionRes
from autobots.conn.stable_diffusion.stable_diffusion import get_stable_diffusion
from autobots.conn.stable_diffusion.text2video.text2video_model import Text2VideoReqModel, Text2VideoScheduler


class Text2VideoRunModel(BaseModel):
    prompt: Optional[str] = Field(None,
                                  description="Text prompt with description of the things you want in the video to be generated.")
    negative_prompt: Optional[str] = Field(default=None, description="Items you don't want in the video.")
    scheduler: Optional[Text2VideoScheduler] = Field(default=Text2VideoScheduler.UniPCMultistepScheduler.value,
                                           description="Use it to set a scheduler for video creation.")
    seconds: Optional[int] = Field(default=3, description="Duration of the video in seconds.")


class ActionCreateText2VideoStableDiffusion(ActionCreate):
    type: ActionType = ActionType.text2video_stable_diffusion
    config: Text2VideoReqModel
    input: Optional[Text2VideoRunModel] = None
    output: Optional[StableDiffusionRes] = None


class ActionText2VideoStableDiffusion(IAction[Text2VideoReqModel, Text2VideoRunModel, StableDiffusionRes]):
    type = ActionType.text2video_stable_diffusion

    def __init__(self, action_config: Text2VideoReqModel):
        self.config = action_config

    async def run_action(self, action_input: Text2VideoRunModel) -> StableDiffusionRes:
        if action_input.prompt: self.config.prompt = f"{self.config.prompt}\n{action_input.prompt}"
        if action_input.negative_prompt: self.config.negative_prompt = f"{self.config.negative_prompt}\n{action_input.negative_prompt}"
        if action_input.scheduler: self.config.scheduler = action_input.scheduler
        if action_input.seconds: self.config.seconds = action_input.seconds
        video = await get_stable_diffusion().text2video(self.config)
        return video

    async def invoke_action(self, input_str: str) -> StableDiffusionRes:
        pass

    @staticmethod
    async def instruction() -> str:
        pass
