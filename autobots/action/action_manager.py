from functools import lru_cache

from autobots.action.action_doc_model import ActionDoc
from autobots.action.action_types import ActionType
from autobots.conn.openai.chat import ChatReq, Message
from autobots.conn.openai.openai import get_openai
from autobots.core.log import log


class ActionManager:

    def __init__(self):
        pass

    @staticmethod
    @lru_cache
    def get_action_types():
        action_types = [action_type for action_type in ActionType]
        return action_types

    async def run_action(self, action: ActionDoc, action_input: Message) -> Message:
        match action.type:
            case ActionType.gen_text_llm_chat_openai:
                return await self._run_gen_text_llm_chat_openai(action, action_input)
            case _:
                log.error("Action Type not found")

    async def _run_gen_text_llm_chat_openai(self, action: ActionDoc, action_input: Message) -> Message:
        chat_req = ChatReq.model_validate(action.input)
        chat_req.messages = chat_req.messages + [action_input]
        chat_res = await get_openai().chat(chat_req=chat_req)
        resp = chat_res.choices[0].message
        return resp


