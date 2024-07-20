from typing import Type, Union
from loguru import logger
from pydantic import HttpUrl, ValidationError, BaseModel

from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.assembly.assemblyai import get_assemblyai
from src.autobots.conn.assembly.assemblyai import TranscriptionReq

class AudioRes(BaseModel):
    url: str


class ActionAudio2TextTranscriptionAssemblyai(
    ActionABC[TranscriptionReq, TranscriptionReq, TranscriptionReq, AudioRes, str]
):
    type = ActionType.audio2text_transcription_assemblyai

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
        return str

    def __init__(self, action_config: TranscriptionReq):
        super().__init__(action_config)

    async def run_action(self, action_input: AudioRes) -> str | None:
        try:
            if self.action_config.file_url is None and action_input.url is None:
                return None
            if action_input.url is not None:
                self.action_config.file_url = HttpUrl(action_input.url)

            transcription = await get_assemblyai().transcribe(self.action_config.file_url)
            return transcription
        except ValidationError as e:
            logger.error(str(e))
        except Exception as e:
            logger.error(str(e))

# Add this line at the end of the file to register the action