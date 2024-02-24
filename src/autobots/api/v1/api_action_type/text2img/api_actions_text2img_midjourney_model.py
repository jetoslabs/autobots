from pydantic import BaseModel

from src.autobots.api.v1.api_action.api_action_model import ActionCreateAPIModel
from src.autobots.conn.useapi.text2img.text2img_model import DiscordJobReqModel, DiscordReqModel


class ActionCreateAPIModelText2ImgMidjourney(ActionCreateAPIModel):
    config: DiscordReqModel



