import io
from typing import Type

from pydantic import HttpUrl, ValidationError

from autobots.action.action.common_action_models import TextObj
from autobots.action.action_type.abc.IAction import IAction, ActionConfigType, ActionInputType, ActionOutputType
from autobots.action.action_type.action_types import ActionType
from autobots.conn.aws.aws_s3 import get_public_s3
from autobots.conn.openai.openai_client import get_openai
from autobots.conn.openai.speech_model import SpeechReq
from autobots.core.log import log
from autobots.core.utils import gen_hash


class ActionText2AudioOpenai(IAction[SpeechReq, TextObj, HttpUrl]):
    type = ActionType.text2text_llm_chat_openai

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return SpeechReq

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return TextObj

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return HttpUrl

    def __init__(self, action_config: SpeechReq):
        super().__init__(action_config)

    async def run_action(self, action_input: TextObj) -> HttpUrl | None:
        try:
            if action_input and action_input.text != "":
                input = f"{self.action_config.input} {action_input.text}"
                self.action_config.input = input
            httpx_binary_response = await get_openai().speech(speech_req=self.action_config)
            if not httpx_binary_response or not httpx_binary_response.content:
                return None
            url = await get_public_s3().put_file_obj(
                io.BytesIO(httpx_binary_response.content),
                f"{gen_hash(self.action_config.input)}.{self.action_config.response_format}"
            )
            return HttpUrl(url)
        except ValidationError as e:
            log.exception(e)
        except Exception as e:
            log.exception(e)
