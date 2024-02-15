from src.autobots.api.v1.api_action.api_action_model import ActionCreateAPIModel
from src.autobots.conn.stable_diffusion.text2video.text2video_model import (
    Text2VideoReqModel,
)


class ActionCreateAPIModelText2VideoStableDiffusion(ActionCreateAPIModel):
    config: Text2VideoReqModel
