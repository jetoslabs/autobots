from typing import Optional, Dict, Any

from pydantic import BaseModel, Field

from autobots.action.action.action_doc_model import ActionCreate, ActionDoc
from autobots.action.action.common_action_models import ImagesRes
from autobots.action.action_type.abc.IAction import IAction
from autobots.action.action_type.action_types import ActionType
from autobots.conn.stable_diffusion.common_models import StableDiffusionRes
from autobots.conn.stable_diffusion.stable_diffusion import get_stable_diffusion
from autobots.conn.stable_diffusion.text2img.text2img_model import Text2ImgReqModel


class Text2ImgRunModel(BaseModel):
    prompt: Optional[str] = Field(default=None,
                                  description="Text prompt with description of the things you want in the image to be generated.")
    negative_prompt: Optional[str] = Field(default=None, description="Items you don't want in the image.")
    width: Optional[int] = Field(default=None, ge=0, le=1024, description="Max Height: Width: 1024x1024.")
    height: Optional[int] = Field(default=None, ge=0, le=1024, description="Max Height: Width: 1024x1024.")
    samples: Optional[int] = Field(default=None, ge=1, le=4,
                                   description="Number of images to be returned in response. The maximum value is 4.")
    webhook: Optional[str] = Field(default=None,
                                   description="Set an URL to get a POST API call once the image generation is complete.")
    track_id: Optional[str] = Field(default=None,
                                    description="This ID is returned in the response to the webhook API call. This will be used to identify the webhook request.")


class ActionCreateText2ImgStableDiffusion(ActionCreate):
    type: ActionType = ActionType.text2img_stable_diffusion
    config: Text2ImgReqModel
    input: Optional[Text2ImgRunModel] = None
    output: Optional[StableDiffusionRes] = None


class ActionText2ImgStableDiffusion(IAction[Text2ImgReqModel, Text2ImgRunModel, StableDiffusionRes]):
    type = ActionType.text2img_stable_diffusion

    def __init__(self, action_config: Text2ImgReqModel):
        super().__init__(action_config)

    @staticmethod
    async def run_action_doc(action_doc: ActionDoc, action_input_dict: Dict[str, Any]) -> StableDiffusionRes:
        action = ActionText2ImgStableDiffusion(Text2ImgReqModel.model_validate(action_doc.config))
        action_output = await action.run_action(Text2ImgRunModel.model_validate(action_input_dict))
        return action_output

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

    async def invoke_action(self, input_str: str) -> StableDiffusionRes:
        pass

    @staticmethod
    async def instruction() -> str:
        pass
