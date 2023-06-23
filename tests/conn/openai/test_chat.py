import pytest as pytest
import pytest_asyncio

from autobots.conn.openai.chat import ChatReq, Message, ChatRes
from autobots.conn.openai.openai import OpenAI
from autobots.core.settings import get_settings


@pytest_asyncio.fixture
async def set_openai():
    settings = get_settings(_env_file='.env.local')
    OpenAI(settings.OPENAI_ORG_ID, settings.OPENAI_API_KEY)


@pytest.mark.asyncio
async def test_chat_happy_path(set_openai):
    msg0 = Message(role="system", content="You are a helpful assistant.")
    msg1 = Message(role="user", content="Most famous Mechanics law")
    params = ChatReq(messages=[msg0, msg1])

    res = await OpenAI.chat(params=params)
    resp: ChatRes = ChatRes(**res.to_dict())

    assert "assistant" == resp.choices[0].message.role
    assert "Newton" in resp.choices[0].message.content
