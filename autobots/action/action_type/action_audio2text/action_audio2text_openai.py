from typing import Type

from openai.types.audio import Transcription
from pydantic import HttpUrl, ValidationError, BaseModel

from autobots.action.action_type.abc.IAction import IAction, ActionConfigType, ActionInputType, ActionOutputType
from autobots.action.action_type.action_types import ActionType
from autobots.conn.openai.openai_client import get_openai
from autobots.conn.openai.transcription_model import TranscriptionReq
from autobots.core.log import log


class AudioRes(BaseModel):
    url: str


class ActionAudio2TextOpenai(IAction[TranscriptionReq, AudioRes, Transcription]):
    type = ActionType.audio2text_openai

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return TranscriptionReq

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return AudioRes

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return Transcription

    def __init__(self, action_config: TranscriptionReq):
        super().__init__(action_config)

    async def run_action(self, action_input: AudioRes) -> Transcription | None:
        try:
            if self.action_config.file_url is None and action_input.url is None:
                return None
            if action_input.url is not None:
                self.action_config.file_url = HttpUrl(action_input.url)

            transcription = await get_openai().transcription(self.action_config)
            return transcription
        except ValidationError as e:
            log.exception(e)
        except Exception as e:
            log.exception(e)
