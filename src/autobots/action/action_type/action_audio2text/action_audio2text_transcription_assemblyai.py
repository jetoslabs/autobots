from typing import Type
from loguru import logger
from pydantic import ValidationError, BaseModel

from src.autobots.action.action.common_action_models import TextObjs, TextObj
from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.assembly.assemblyai import get_assemblyai
from src.autobots.conn.assembly.assemblyai import TranscriptionReq

class AudioRes(BaseModel):
    text: str

class AudioUrl(BaseModel):
    text: str

class ActionAudio2TextTranscriptionAssemblyai(
    ActionABC[TranscriptionReq, TranscriptionReq, TranscriptionReq, AudioUrl, TextObjs]
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
        return AudioUrl

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return TextObjs

    def __init__(self, action_config: TranscriptionReq):
        super().__init__(action_config)

    async def run_action(self, action_input: AudioUrl) -> TextObjs | None:
        try:
            if self.action_config.file_url is None and action_input.text is None:
                return None
            if action_input.text is not None:
                self.action_config.file_url = (action_input.text)

            # Convert the text to a string before passing it to transcribe
            file_url_str = str(self.action_config.file_url)
            transcription = await get_assemblyai().transcribe(file_url_str)
            if transcription is None:
                return None
            return TextObjs(texts=[TextObj(text=transcription)])
        except ValidationError as e:
            logger.error(str(e))
        except Exception as e:
            logger.error(str(e))

# Add this line at the end of the file to register the action