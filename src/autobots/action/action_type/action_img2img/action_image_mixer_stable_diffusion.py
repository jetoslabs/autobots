from typing import Optional, Type

from pydantic import Field, BaseModel

from src.autobots.action.action.action_doc_model import ActionCreate
from src.autobots.action.action_type.abc.IAction import IAction, ActionOutputType, ActionInputType, ActionConfigType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.stable_diffusion.common_models import StableDiffusionRes
from src.autobots.conn.stable_diffusion.image_mixer.image_mixer_model import ImageMixerReqModel
from src.autobots.conn.stable_diffusion.stable_diffusion import get_stable_diffusion


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


class ActionImageMixerStableDiffusion(
    IAction[ImageMixerReqModel, ImageMixerReqModel, ImageMixerReqModel, ImageMixerRunModel, StableDiffusionRes]
):
    type = ActionType.image_mixer_stable_diffusion

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return ImageMixerReqModel

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return ImageMixerReqModel

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return ImageMixerReqModel

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return ImageMixerRunModel

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return StableDiffusionRes

    def __init__(self, action_config: ImageMixerReqModel):
        super().__init__(action_config)

    async def run_action(self, action_input: ImageMixerRunModel) -> StableDiffusionRes:
        if action_input.prompt:
            self.action_config.prompt = f"{self.action_config.prompt}\n{action_input.prompt}"
        if action_input.negative_prompt:
            self.action_config.negative_prompt = f"{self.action_config.negative_prompt}\n{action_input.negative_prompt}"
        if action_input.init_image:
            self.action_config.init_image = f"{self.action_config.init_image},{action_input.init_image}"
        if action_input.init_image_weights:
            self.action_config.init_image_weights = f"{self.action_config.init_image_weights},{action_input.init_image_weights}"
        if action_input.width:
            self.action_config.width = action_input.width
        if action_input.height:
            self.action_config.height = action_input.height
        if action_input.seed:
            self.action_config.seed = action_input.seed
        if action_input.samples:
            self.action_config.height = action_input.samples
        if action_input.webhook:
            self.action_config.webhook = action_input.webhook
        if action_input.track_id:
            self.action_config.track_id = action_input.track_id
        images = await get_stable_diffusion().image_mixer(self.action_config)
        return images
