import io
from typing import Type

from loguru import logger
from pydantic import HttpUrl, ValidationError, BaseModel

from src.autobots.action.action.common_action_models import TextObj
from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.aws.aws_s3 import get_public_s3
from src.autobots.conn.openai.openai_client import get_openai
from src.autobots.conn.openai.openai_audio.speech_model import SpeechReq
from src.autobots.core.utils import gen_hash
from src.autobots.data_model.context import Context
from src.autobots.user.user_orm_model import UserORM


class AudioRes(BaseModel):
    url: str


class ActionText2AudioSpeechOpenai(ActionABC[SpeechReq, SpeechReq, SpeechReq, TextObj, AudioRes]):
    type = ActionType.text2audio_speech_openai

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return SpeechReq

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return SpeechReq

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return SpeechReq

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return TextObj

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return AudioRes

    def __init__(self, action_config: SpeechReq, user: UserORM | None = None):
        super().__init__(action_config=action_config, user=user)

    async def run_action(self, ctx: Context, action_input: TextObj) -> AudioRes | None:
        try:
            if action_input and action_input.text != "":
                input = f"{self.action_config.input} {action_input.text}"
                self.action_config.input = input
            httpx_binary_response = await get_openai().openai_audio.speech(speech_req=self.action_config)
            if not httpx_binary_response or not httpx_binary_response.content:
                return None
            url = await get_public_s3().put_file_obj(
                io.BytesIO(httpx_binary_response.content),
                f"{gen_hash(self.action_config.input)}.{self.action_config.response_format}"
            )
            http_url = HttpUrl(url)
            return AudioRes(url=str(http_url))
        except ValidationError as e:
            logger.error(str(e))
        except Exception as e:
            logger.error(str(e))
