from typing import Optional, List

from pydantic import ValidationError

from autobots.action.action_type.abc.IAction import IAction
from autobots.action.action.action_doc_model import ActionCreate
from autobots.action.action_type.action_types import ActionType
from autobots.action.action.common_action_models import TextObj, TextObjs
from autobots.conn.openai.chat import Message, ChatReq, Role
from autobots.conn.openai.openai import get_openai
from autobots.core.log import log


class ActionCreateGenTextLlmChatOpenai(ActionCreate):
    type: ActionType = ActionType.text2text_llm_chat_openai
    config: ChatReq
    input: Optional[TextObj] = None
    output: Optional[TextObjs] = None


class ActionGenTextLlmChatOpenaiV2(IAction[ChatReq, TextObj, TextObjs]):
    type = ActionType.text2text_llm_chat_openai

    def __init__(self, action_config: ChatReq):
        self.chat_req = action_config

    async def run_action(self, action_input: TextObj) -> TextObjs:
        text_objs = TextObjs(texts=[])
        try:
            if action_input and action_input.text != "":
                message = Message(role=Role.user, content=action_input.text)
                self.chat_req.messages = self.chat_req.messages + [message]
            chat_res = await get_openai().chat(chat_req=self.chat_req)
            if not chat_res:
                return text_objs
            # resp = Message.model_validate(chat_res.choices[0].message)
            for choice in chat_res.choices:
                text_objs.texts.append(TextObj(text=choice.message.content))
            return text_objs
        except ValidationError as e:
            log.exception(e)

    async def invoke_action(self, input_str: str) -> Message:
        pass

    @staticmethod
    async def instruction() -> str:
        pass
