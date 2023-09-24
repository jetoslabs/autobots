from autobots.action.IActionGenText import IActionGenText
from autobots.action.action_doc_model import ActionCreate
from autobots.action.action_types import ActionType
from autobots.conn.openai.chat import Message, ChatReq, Role
from autobots.conn.openai.openai import get_openai
from autobots.prompts.user_prompts import Input


class ActionCreateGenTextLlmChatOpenai(ActionCreate):
    type: ActionType = ActionType.gen_text_llm_chat_openai
    input: ChatReq


class ActionGenTextLlmChatOpenaiV2(IActionGenText):
    type = ActionType.gen_text_llm_chat_openai

    def __init__(self, action_data: ChatReq):
        self.chat_req = action_data

    async def run_action(self, action_input: Input) -> Message:
        if action_input and action_input.input != "":
            message = Message(role=Role.user, content=action_input.input)
            self.chat_req.messages = self.chat_req.messages + [message]
        chat_res = await get_openai().chat(chat_req=self.chat_req)
        resp = chat_res.choices[0].message
        return resp

    async def invoke_action(self, input_str: str) -> Message:
        pass

    @staticmethod
    async def instruction() -> str:
        pass