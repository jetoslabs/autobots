from typing import Optional, Type

from pydantic import BaseModel, Field

from autobots.action.action.action_doc_model import ActionCreate
from autobots.action.action_type.abc.IAction import IAction, ActionOutputType, ActionInputType, ActionConfigType
from autobots.action.action_type.action_types import ActionType
from autobots.conn.stable_diffusion.common_models import StableDiffusionRes
from autobots.conn.stable_diffusion.stable_diffusion import get_stable_diffusion
from autobots.conn.stable_diffusion.text2img.text2img_model import Text2ImgReqModel


class Text2ImgRunModel(BaseModel):
    prompt: Optional[str] = Field(default=None,
                                  description="Text prompt with description of the things you want in the image to be generated.")


class ActionCreateText2ImgStableDiffusion(ActionCreate):
    type: ActionType = ActionType.text2img_midjourney_ai
    config: Text2ImgReqModel


class ActionText2ImgMidjourney(IAction[Text2ImgReqModel, Text2ImgRunModel, StableDiffusionRes]):
    type = ActionType.text2img_midjourney_ai

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return Text2ImgReqModel

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return Text2ImgRunModel

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return StableDiffusionRes

    def __init__(self, action_config: Text2ImgReqModel):
        super().__init__(action_config)

    async def run_action(self, action_input: Text2ImgRunModel) -> StableDiffusionRes:
        if action_input.prompt: self.action_config.prompt = f"{self.action_config.prompt}\n{action_input.prompt}"
        if action_input.negative_prompt:
            self.action_config.negative_prompt = f"{self.action_config.negative_prompt}\n{action_input.negative_prompt}"
        if action_input.width: self.action_config.width = action_input.width
        if action_input.height: self.action_config.height = action_input.height
        if action_input.samples: self.action_config.samples = action_input.samples
        if action_input.webhook: self.action_config.webhook = action_input.webhook
        if action_input.track_id: self.action_config.track_id = action_input.track_id
        images = await get_stable_diffusion().text2img(self.action_config)
        return images
