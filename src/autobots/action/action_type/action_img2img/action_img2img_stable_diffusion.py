from typing import Type, Optional

from pydantic import BaseModel, Field

from src.autobots.action.action_type.abc.IAction import IAction, ActionConfigType, ActionInputType, ActionOutputType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.stable_diffusion.common_models import StableDiffusionRes
from src.autobots.conn.stable_diffusion.img2img.img2img_model import SDImg2ImgReqModel
from src.autobots.conn.stable_diffusion.stable_diffusion import get_stable_diffusion


class Img2ImgRunModel(BaseModel):
    prompt: Optional[str] = Field(None,
                                  description="Text prompt with description of the things you want in the image to be generated")
    negative_prompt: Optional[str] = Field(default=None, description="Items you don't want in the image")
    init_image: Optional[str] = Field(None, description="Link to the Initial Image")
    width: Optional[int] = Field(default=None, ge=1, le=1024,
                                 description="Width of the image. Max Height: Width: 1024x1024")
    height: Optional[int] = Field(default=None, ge=1, le=1024,
                                  description="Height of the image. Max Height: Width: 1024x1024")
    samples: Optional[int] = Field(default=None, ge=1, le=4,
                                   description="Number of images to be returned in response. The maximum value is 4.")
    strength: float | None = Field(None, ge=0.0, le=1.0,
                                   description="Prompt strength when using init image. 1.0 corresponds to full destruction of information in the init image.")
    seed: Optional[int] = Field(None,
                                description="Seed is used to reproduce results, same seed will give you same image in return again. Pass null for a random number.")
    webhook: Optional[str] = Field(default=None,
                                   description="Set an URL to get a POST API call once the image generation is complete.")
    track_id: Optional[str] = Field(default=None,
                                    description="This ID is returned in the response to the webhook API call. This will be used to identify the webhook request.")


class ActionImg2ImgStableDiffusion(IAction[SDImg2ImgReqModel, Img2ImgRunModel, StableDiffusionRes]):
    type = ActionType.img2img_stable_diffusion

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return SDImg2ImgReqModel

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return Img2ImgRunModel

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return StableDiffusionRes

    def __init__(self, action_config: SDImg2ImgReqModel):
        super().__init__(action_config)

    async def run_action(self, action_input: Img2ImgRunModel) -> StableDiffusionRes:
        if action_input.prompt: self.action_config.prompt = f"{self.action_config.prompt}\n{action_input.prompt}"
        if action_input.negative_prompt: self.action_config.negative_prompt = f"{self.action_config.negative_prompt}\n{action_input.negative_prompt}"
        if action_input.init_image: self.action_config.init_image = action_input.init_image
        if action_input.width: self.action_config.width = action_input.width
        if action_input.height: self.action_config.height = action_input.height
        if action_input.samples: self.action_config.height = action_input.samples
        if action_input.strength: self.action_config.strength = action_input.strength
        if action_input.seed: self.action_config.seed = action_input.seed
        if action_input.webhook: self.action_config.webhook = action_input.webhook
        if action_input.track_id: self.action_config.track_id = action_input.track_id
        images = await get_stable_diffusion().img2img(self.action_config)
        return images
