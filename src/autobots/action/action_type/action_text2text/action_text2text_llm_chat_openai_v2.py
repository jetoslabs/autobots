from typing import Type

from loguru import logger
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam
from pydantic import ValidationError

from src.autobots.action.action_type.abc.IAction import IAction, ActionOutputType, ActionInputType, ActionConfigType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.action.action.common_action_models import TextObj, TextObjs
from src.autobots.conn.openai.openai_chat.chat_model import Message, ChatReq, Role
from src.autobots.conn.openai.openai_client import get_openai


class ActionText2TextLlmChatOpenai(IAction[ChatReq, ChatReq, ChatReq, TextObj, TextObjs]):
    type = ActionType.text2text_llm_chat_openai

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return ChatReq

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return ChatReq

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

    @staticmethod
    async def update_config_with_prev_IO(
            curr_config: ChatReq,
            prev_input: TextObj | None = None,
            prev_output: TextObjs | None = None,
    ) -> ChatReq:
        #     ChatCompletionUserMessageParam,
        #     ChatCompletionAssistantMessageParam,
        if not prev_input or not prev_output or prev_input.text == "" or len(prev_output.texts) == 0 :
            return curr_config
        updated_messages = (
                curr_config.messages +
                [ChatCompletionUserMessageParam(role="user", content=prev_input.text)] +
                [ChatCompletionAssistantMessageParam(role="assistant", content=prev_output_text_obj.text) for prev_output_text_obj in prev_output.texts]
        )
        curr_config.messages = updated_messages
        return curr_config



    async def run_action(self, action_input: TextObj) -> TextObjs:
        text_objs = TextObjs(texts=[])
        try:
            if action_input and action_input.text != "":
                message = Message(role=Role.user.value, content=action_input.text)
                self.action_config.messages = self.action_config.messages + [message]
            chat_res = await get_openai().openai_chat.chat(chat_req=self.action_config)
            # remove input message from Config messages
            self.action_config.messages.pop()
            if not chat_res:
                return text_objs
            # resp = Message.model_validate(chat_res.choices[0].message)
            for choice in chat_res.choices:
                text_objs.texts.append(TextObj(text=choice.message.content))
            return text_objs
        except ValidationError as e:
            logger.error(str(e))
