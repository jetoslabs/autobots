
from src.autobots.api.v1.api_action.api_action_model import ActionCreateAPIModel
from src.autobots.conn.useapi.text2img.text2img_model import DiscordReqModel


class ActionCreateAPIModelText2ImgMidjourney(ActionCreateAPIModel):
    config: DiscordReqModel



