
from autobots.action.action_doc_model import ActionDoc, ActionCreate
from autobots.action.action_types import ActionType
from autobots.conn.openai.chat import Message, ChatReq, Role
from autobots.conn.openai.openai import get_openai
from autobots.prompts.user_prompts import Input


class ActionCreateGenTextLlmChatOpenai(ActionCreate):
    type: ActionType = ActionType.gen_text_llm_chat_openai
    input: ChatReq


class ActionGenTextLlmChatOpenai:
    type = ActionType.gen_text_llm_chat_openai

    def __init__(self):
        pass

    @staticmethod
    async def run(action: ActionDoc, action_input: Input) -> Message:
        chat_req = ChatReq.model_validate(action.input)
        message = Message(role=Role.user, content=action_input.input)
        chat_req.messages = chat_req.messages + [message]
        chat_res = await get_openai().chat(chat_req=chat_req)
        resp = chat_res.choices[0].message
        return resp

    async def output_to_input(self, message: Message) -> Input:
        pass
