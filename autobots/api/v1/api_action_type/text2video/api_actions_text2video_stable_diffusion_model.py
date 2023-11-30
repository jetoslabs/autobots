from autobots.api.v1.api_action.api_action_model import ActionCreateAPIModel
from autobots.conn.stable_diffusion.text2video.text2video_model import Text2VideoReqModel


class ActionCreateAPIModelText2VideoStableDiffusion(ActionCreateAPIModel):
    config: Text2VideoReqModel
