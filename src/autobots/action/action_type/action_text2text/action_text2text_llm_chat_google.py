from typing import Type

from loguru import logger
from pydantic import ValidationError

from src.autobots.action.action.common_action_models import TextObj, TextObjs
from src.autobots.action.action_type.abc.IAction import (
    ActionConfigType,
    ActionInputType,
    ActionOutputType,
    IAction,
)
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.google.google_genai_chat.chat_model import (
    ChatReq,
    ContentDict,
    Role,
)
from src.autobots.conn.google.google_genai_client import get_google_genai


class ActionText2TextLlmChatGoogleGenAI(IAction[ChatReq, TextObj, TextObjs]):
    type = ActionType.text2text_llm_chat_google_genai

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return ChatReq

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return TextObj

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return TextObjs

    def __init__(self, action_config: ChatReq):
        super().__init__(action_config)

    async def run_action(self, action_input: TextObj) -> TextObjs:
        text_objs = TextObjs(texts=[])
        try:
            if action_input and action_input.text != "":
                content_dict = ContentDict(role=Role.user, parts=[action_input.text])
                self.action_config.contents = self.action_config.contents + [
                    content_dict
                ]
            chat_res = await get_google_genai().google_genai_chat.chat(
                chat_req=self.action_config
            )
            if not chat_res:
                return text_objs

            response_text = ""
            async for part in chat_res:
                response_text += part.text
            text_objs.texts.append(response_text)
            return text_objs
        except ValidationError as e:
            logger.error(str(e))
