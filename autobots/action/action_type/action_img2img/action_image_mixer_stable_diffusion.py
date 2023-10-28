from typing import Optional

from pydantic import Field, BaseModel

from autobots.action.action.action_doc_model import ActionCreate
from autobots.action.action_type.abc.IAction import IAction
from autobots.action.action_type.action_types import ActionType
from autobots.conn.stable_diffusion.common_models import StableDiffusionRes
from autobots.conn.stable_diffusion.image_mixer.image_mixer_model import ImageMixerReqModel
from autobots.conn.stable_diffusion.stable_diffusion import get_stable_diffusion


class ImageMixerRunModel(BaseModel):
    prompt: Optional[str] = Field(None,
                                  description="Text prompt with description of the things you want in the image to be generated")
    negative_prompt: Optional[str] = Field(default=None, description="Items you don't want in the image")
    init_image: Optional[str] = Field(None, description="comma separated image urls of images to mix")
    init_image_weights: Optional[str] = Field(None,
                                              description="weight of the images being passed separated by comma. Min 0 and Max 1")
    width: Optional[int] = Field(default=None, ge=1, le=1024, description="Width of the image. Max Height: Width: 1024x1024")
    height: Optional[int] = Field(default=None, ge=1, le=1024, description="Height of the image. Max Height: Width: 1024x1024")
    seed: Optional[int] = Field(None,
                                description="Seed is used to reproduce results, same seed will give you same image in return again. Pass null for a random number.")
    samples: Optional[int] = Field(default=None, ge=1, le=4,
                         description="Number of images to be returned in response. The maximum value is 4.")
    webhook: Optional[str] = Field(default=None,
                                   description="Set an URL to get a POST API call once the image generation is complete.")
    track_id: Optional[str] = Field(default=None,
                                    description="This ID is returned in the response to the webhook API call. This will be used to identify the webhook request.")


class ActionCreateImageMixerStableDiffusion(ActionCreate):
    type: ActionType = ActionType.image_mixer_stable_diffusion
    config: ImageMixerReqModel
    input: Optional[ImageMixerRunModel] = None
    output: Optional[StableDiffusionRes] = None


class ActionImageMixerStableDiffusion(IAction[ImageMixerReqModel, ImageMixerRunModel, StableDiffusionRes]):
    type = ActionType.image_mixer_stable_diffusion

    def __init__(self, action_config: ImageMixerReqModel):
        self.config = action_config

    async def run_action(self, action_input: ImageMixerRunModel) -> StableDiffusionRes:
        if action_input.prompt: self.config.prompt = f"{self.config.prompt}\n{action_input.prompt}"
        if action_input.negative_prompt: self.config.negative_prompt = f"{self.config.negative_prompt}\n{action_input.negative_prompt}"
        if action_input.init_image: self.config.init_image = f"{self.config.init_image},{action_input.init_image}"
        if action_input.init_image_weights: self.config.init_image_weights = f"{self.config.init_image_weights},{action_input.init_image_weights}"
        if action_input.width: self.config.width = action_input.width
        if action_input.height: self.config.height = action_input.height
        if action_input.seed: self.config.seed = action_input.seed
        if action_input.samples: self.config.height = action_input.samples
        if action_input.webhook: self.config.webhook = action_input.webhook
        if action_input.track_id: self.config.track_id = action_input.track_id
        images = await get_stable_diffusion().image_mixer(self.config)
        return images

    async def invoke_action(self, input_str: str) -> StableDiffusionRes:
        pass

    @staticmethod
    async def instruction() -> str:
        pass
