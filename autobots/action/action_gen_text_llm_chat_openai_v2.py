from autobots.action.IActionGenText import IActionGenText
from autobots.action.action_doc_model import ActionCreate
from autobots.action.action_types import ActionType
from autobots.conn.openai.chat import Message, ChatReq, Role
from autobots.conn.openai.openai import get_openai
from autobots.prompts.user_prompts import TextObj


class ActionCreateGenTextLlmChatOpenai(ActionCreate):
    type: ActionType = ActionType.gen_text_llm_chat_openai
    config: ChatReq
    input: TextObj = TextObj()
    output: TextObj = TextObj()


class ActionGenTextLlmChatOpenaiV2(IActionGenText):
    type = ActionType.gen_text_llm_chat_openai

    def __init__(self, action_data: ChatReq):
        self.chat_req = action_data

    async def run_action(self, action_input: TextObj) -> Message:
        if action_input and action_input.text != "":
            message = Message(role=Role.user, content=action_input.text)
            self.chat_req.messages = self.chat_req.messages + [message]
        chat_res = await get_openai().chat(chat_req=self.chat_req)
        resp = chat_res.choices[0].message
        return resp

    async def invoke_action(self, input_str: str) -> Message:
        pass

    @staticmethod
    async def instruction() -> str:
        pass