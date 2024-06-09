from typing import Type

from loguru import logger
from openai.types.audio import Translation
from pydantic import BaseModel, HttpUrl, ValidationError

from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.openai.openai_client import get_openai
from src.autobots.conn.openai.openai_audio.translation_model import TranslationReq


class AudioRes(BaseModel):
    url: str


class ActionAudio2TextTranslationOpenai(ActionABC[TranslationReq, TranslationReq, TranslationReq, AudioRes, Translation]):
    type = ActionType.audio2text_translation_openai

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return TranslationReq

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return TranslationReq

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return TranslationReq

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return AudioRes

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return Translation

    def __init__(self, action_config: TranslationReq):
        super().__init__(action_config)

    async def run_action(self, action_input: AudioRes) -> Translation | None:
        try:
            if self.action_config.file_url is None and action_input.url is None:
                return None
            if action_input.url is not None:
                self.action_config.file_url = HttpUrl(action_input.url)

            translation = await get_openai().openai_audio.translation(self.action_config)
            return translation
        except ValidationError as e:
            logger.error(str(e))
        except Exception as e:
            logger.error(str(e))
