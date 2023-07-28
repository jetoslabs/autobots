from typing import List

from autobots.conn.openai.chat import Message, ChatReq
from autobots.conn.openai.openai import get_openai, OpenAI
from autobots.core import settings
from autobots.core.settings import get_settings


class Prompt:

    @staticmethod
    async def chat_openai(
            messages: List[Message],
            llm: OpenAI = get_openai(settings=get_settings())
    ) -> Message:
        chat_req = ChatReq(messages=messages)
        chat_res = await llm.chat(chat_req=chat_req)
        return chat_res.choices[0].message
