import pytest as pytest

from autobots.conn.openai.chat import ChatReq, Message, ChatRes
from autobots.conn.openai.openai import get_openai

@pytest.mark.asyncio
async def test_chat_happy_path(set_test_settings):
    msg0 = Message(role="system", content="You are a helpful assistant.")
    msg1 = Message(role="user", content="Most famous Mechanics law")
    params = ChatReq(messages=[msg0, msg1])

    resp: ChatRes = await get_openai().chat(chat_req=params)

    assert "assistant" == resp.choices[0].message.role
    assert "Newton" in resp.choices[0].message.content
