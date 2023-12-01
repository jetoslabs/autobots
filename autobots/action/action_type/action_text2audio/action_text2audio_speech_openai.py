import io
from typing import Type

from pydantic import HttpUrl, ValidationError, BaseModel

from autobots.action.action.common_action_models import TextObj
from autobots.action.action_type.abc.IAction import IAction, ActionConfigType, ActionInputType, ActionOutputType
from autobots.action.action_type.action_types import ActionType
from autobots.conn.aws.aws_s3 import get_public_s3
from autobots.conn.openai.openai_client import get_openai
from autobots.conn.openai.openai_audio.speech_model import SpeechReq
from autobots.core.logging.log import Log
from autobots.core.utils import gen_hash


class AudioRes(BaseModel):
    url: str


class ActionText2AudioSpeechOpenai(IAction[SpeechReq, TextObj, AudioRes]):
    type = ActionType.text2audio_speech_openai

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return SpeechReq

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return TextObj

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return AudioRes

    def __init__(self, action_config: SpeechReq):
        super().__init__(action_config)

    async def run_action(self, action_input: TextObj) -> AudioRes | None:
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
            Log.error(str(e))
        except Exception as e:
            Log.error(str(e))
