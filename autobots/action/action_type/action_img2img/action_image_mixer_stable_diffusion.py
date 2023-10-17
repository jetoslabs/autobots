from autobots.action.action_doc_model import ActionCreate
from autobots.action.action_type.IActionGenImage import IActionGenImage
from autobots.action.action_type.action_types import ActionType
from autobots.conn.stable_diffusion.common_models import StableDiffusionRes
from autobots.conn.stable_diffusion.image_mixer import ImageMixerReqModel
from autobots.conn.stable_diffusion.stable_diffusion import get_stable_diffusion


class ActionCreateImgMixerStableDiffusion(ActionCreate):
    type: ActionType = ActionType.image_mixer_stable_diffusion
    config: ImageMixerReqModel
    input: ImageMixerReqModel
    output: StableDiffusionRes


class ActionImageMixerStableDiffusion(IActionGenImage):
    type = ActionType.image_mixer_stable_diffusion

    def __init__(self, action_config: ImageMixerReqModel):
        self.config = action_config

    async def run_action(self, action_input: ImageMixerReqModel) -> StableDiffusionRes:
        # self.image_req.prompt = f"{self.image_req.prompt}\n{action_input.text}"
        images = await get_stable_diffusion().image_mixer(action_input)
        return images

    async def invoke_action(self, input_str: str) -> StableDiffusionRes:
        pass

    @staticmethod
    async def instruction() -> str:
        pass
