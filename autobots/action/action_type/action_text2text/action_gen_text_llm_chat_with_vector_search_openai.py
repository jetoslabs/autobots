from typing import List, Optional

from pydantic import BaseModel

from autobots.action.action_type.abc.IAction import IAction
from autobots.action.action.action_doc_model import ActionCreate
from autobots.action.action_type.action_types import ActionType
from autobots.action.action.common_action_models import TextObj
from autobots.conn.openai.chat import Message, ChatReq, Role
from autobots.conn.openai.openai import get_openai
from autobots.datastore.datastore import Datastore


class ActionCreateGenTextLlmChatWithVectorSearchOpenaiInput(BaseModel):
    datastore_id: str
    chat_req: ChatReq
    input: Optional[TextObj] = None
    output: Optional[List[TextObj]] = None


class ActionCreateGenTextLlmChatWithVectorSearchOpenai(ActionCreate):
    type: ActionType = ActionType.gen_text_llm_chat_with_vector_search_openai
    config: ActionCreateGenTextLlmChatWithVectorSearchOpenaiInput


class ActionGenTextLlmChatWithVectorSearchOpenai(IAction[ActionCreateGenTextLlmChatWithVectorSearchOpenai, TextObj, List[TextObj]]):
    """
    Vector search and add it to chat prompt as context
    """
    type = ActionType.gen_text_llm_chat_with_vector_search_openai

    def __init__(self, action_config: ActionCreateGenTextLlmChatWithVectorSearchOpenai):
        self.action_data = action_config
        self.datastore = Datastore().hydrate(datastore_id=action_config.config.datastore_id)

    async def run_action(self, action_input: TextObj) -> List[TextObj] | None:
        # vector search
        search_results = await self.datastore.search(action_input.text, top_k=3)
        if len(search_results) == 0:
            return None
        context = "Only use relevant context to give response. If the context is insufficient say \"Cannot answer from given context\"\nContext: \n"
        for result in search_results:
            context = f"{context}{result}\n"
        # LM chat
        message = Message(role=Role.user, content=f"{context}Question: {action_input.text}")
        self.action_data.input.messages = self.action_data.config.chat_req.messages + [message]
        chat_res = await get_openai().chat(chat_req=self.action_data.config.chat_req)
        resp = chat_res.choices[0].message
        return [TextObj(text=resp)]

    async def invoke_action(self, input_str: str) -> Message:
        pass

    @staticmethod
    async def instruction() -> str:
        pass
