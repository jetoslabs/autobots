from typing import Type, Optional

from pydantic import BaseModel, Field

from src.autobots.action.action_type.abc.IAction import IAction, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.replicate.virtual_try_on.virtual_try_on import VirtualTryOnDiffusionInParams, VirtualTryOnOutputData
from src.autobots.conn.replicate.replicate import get_replicate


class Img2ImgRunModelVirtualTryOn(BaseModel):
    model_image: Optional[str] = Field(None,
                                  description="imange url")
    garment_image: Optional[str] = Field(default=None, description="garmemt image")
    steps: Optional[int] = Field(20, description="Steps", ge=1, le=40)
    guidance_scale: Optional[int] = Field(default=2, ge=1, le=5,
                                 description="guidance scale")
    seed: Optional[int] = Field(default=None, ge=0, le=18446744073709552000,
                                  description="seed")

class ActionImg2ImgVirtualTryOn(
    IAction[VirtualTryOnDiffusionInParams, VirtualTryOnDiffusionInParams, VirtualTryOnDiffusionInParams, Img2ImgRunModelVirtualTryOn, VirtualTryOnOutputData]
):
    type = ActionType.img2img_virtual_try_on

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return VirtualTryOnDiffusionInParams

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return VirtualTryOnDiffusionInParams

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return VirtualTryOnDiffusionInParams

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return Img2ImgRunModelVirtualTryOn

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return VirtualTryOnOutputData

    def __init__(self, action_config: VirtualTryOnDiffusionInParams):
        super().__init__(action_config)

    async def run_action(self, action_input: Img2ImgRunModelVirtualTryOn) -> VirtualTryOnOutputData:
        if action_input.model_image:
            self.action_config.model_image = f"{action_input.model_image}"
        if action_input.garment_image:
            self.action_config.garment_image = f"{action_input.garment_image}"
        if action_input.steps:
            self.action_config.steps = action_input.steps
        if action_input.guidance_scale:
            self.action_config.guidance_scale = action_input.guidance_scale
        if action_input.seed:
            self.action_config.seede = action_input.seed
        images = await get_replicate().virtual_try_on.run(self.action_config)
        return images
