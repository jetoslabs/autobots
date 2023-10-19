from pydantic import BaseModel

from autobots.api.v1.api_actions.api_action_model import ActionCreateAPIModel
from autobots.conn.stable_diffusion.text2img.text2img_model import Text2ImgReqModel


class ActionCreateAPIModelText2ImgStableDiffusion(ActionCreateAPIModel):
    config: Text2ImgReqModel


# class ActionRunAPIModelText2ImgStableDiffusion(BaseModel):
#     config: Text2ImgReqModel
