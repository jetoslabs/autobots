from autobots.action.action_doc_model import ActionCreate
from autobots.action.action_type.IActionGenImage import IActionGenImage
from autobots.action.action_type.action_types import ActionType
from autobots.conn.stable_diffusion.common_models import StableDiffusionRes
from autobots.conn.stable_diffusion.stable_diffusion import get_stable_diffusion
from autobots.conn.stable_diffusion.text2video.text2video_model import Text2VideoReqModel


class ActionCreateText2VideoStableDiffusion(ActionCreate):
    type: ActionType = ActionType.text2video_stable_diffusion
    config: Text2VideoReqModel
    input: Text2VideoReqModel
    output: StableDiffusionRes


class ActionText2VideoStableDiffusion(IActionGenImage):
    type = ActionType.text2video_stable_diffusion

    def __init__(self, action_config: Text2VideoReqModel):
        self.config = action_config

    async def run_action(self, action_input: Text2VideoReqModel) -> StableDiffusionRes:
        # self.image_req.prompt = f"{self.image_req.prompt}\n{action_input.text}"
        video = await get_stable_diffusion().text2video(action_input)
        return video

    async def invoke_action(self, input_str: str) -> StableDiffusionRes:
        pass

    @staticmethod
    async def instruction() -> str:
        pass
