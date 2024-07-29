from typing import Type

from loguru import logger
from openai.types.audio import Transcription
from pydantic import HttpUrl, ValidationError, BaseModel

from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.openai.openai_client import get_openai
from src.autobots.conn.openai.openai_audio.transcription_model import TranscriptionReq
from src.autobots.data_model.context import Context
from src.autobots.user.user_orm_model import UserORM


class AudioRes(BaseModel):
    url: str


class ActionAudio2TextTranscriptionOpenai(
    ActionABC[TranscriptionReq, TranscriptionReq, TranscriptionReq, AudioRes, Transcription]
):
    type = ActionType.audio2text_transcription_openai

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return TranscriptionReq

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return TranscriptionReq

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return TranscriptionReq

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return AudioRes

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return Transcription

    def __init__(self, action_config: TranscriptionReq, user: UserORM | None = None):
        super().__init__(action_config=action_config, user=user)

    async def run_action(self, ctx: Context, action_input: AudioRes) -> Transcription | None:
        try:
            if self.action_config.file_url is None and action_input.url is None:
                return None
            if action_input.url is not None:
                self.action_config.file_url = HttpUrl(action_input.url)

            transcription = await get_openai().openai_audio.transcription(self.action_config)
            return transcription
        except ValidationError as e:
            logger.error(str(e))
        except Exception as e:
            logger.error(str(e))
