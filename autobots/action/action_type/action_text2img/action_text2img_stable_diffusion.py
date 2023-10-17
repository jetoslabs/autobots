from autobots.action.action_doc_model import ActionCreate
from autobots.action.action_type.IActionGenImage import IActionGenImage
from autobots.action.action_type.action_types import ActionType
from autobots.conn.stable_diffusion.common_models import StableDiffusionRes
from autobots.conn.stable_diffusion.stable_diffusion import get_stable_diffusion
from autobots.conn.stable_diffusion.text2img import Text2ImgReqModel


class ActionCreateText2ImgStableDiffusion(ActionCreate):
    type: ActionType = ActionType.text2img_stable_diffusion
    config: Text2ImgReqModel
    input: Text2ImgReqModel
    output: StableDiffusionRes


class ActionText2ImgStableDiffusion(IActionGenImage):
    type = ActionType.text2img_stable_diffusion

    def __init__(self, action_data: Text2ImgReqModel):
        self.image_req = action_data

    async def run_action(self, action_input: Text2ImgReqModel) -> StableDiffusionRes:
        # self.image_req.prompt = f"{self.image_req.prompt}\n{action_input.text}"
        images = await get_stable_diffusion().text2img(action_input)
        return images

    async def invoke_action(self, input_str: str) -> StableDiffusionRes:
        pass

    @staticmethod
    async def instruction() -> str:
        pass
