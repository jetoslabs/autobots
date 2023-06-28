from typing import List

from autobots.action.action import Action, ActionData
from autobots.conn.conn import get_conn
from autobots.conn.openai.chat import Message, ChatReq, ChatRes


class LLMChatData(ActionData):
    chat_req: ChatReq
    context: List[Message] = []


class LLMChat(Action):

    async def run(self, action_data: LLMChatData, *args, **kwargs):
        # add initial user message to context
        action_data.context = action_data.context + action_data.chat_req.messages
        res: ChatRes = await get_conn().open_ai.chat(action_data.chat_req)
        # add response message to context
        [action_data.context.append(choice.message) for choice in res.choices]
        # action_data.context = action_data.context + res
        return action_data  # Don't return action_data as it is not new, same input object is modified
