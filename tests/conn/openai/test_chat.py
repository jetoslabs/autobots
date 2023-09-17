import pytest as pytest
import pytest_asyncio

from autobots.conn.openai.chat import ChatReq, Message, ChatRes
from autobots.conn.openai.openai import get_openai
from autobots.core.settings import get_settings


# Run command `python -m pytest -s` from `autobots/tests` folder
@pytest_asyncio.fixture
async def set_openai():
    settings = get_settings(_env_file='../.env.local')
    # settings.OPENAI_ENGINE = "gpt-3.5-turbo-16k-0613"


@pytest.mark.asyncio
async def test_chat_happy_path(set_openai):
    msg0 = Message(role="system", content="You are a helpful assistant.")
    msg1 = Message(role="user", content="Most famous Mechanics law")
    params = ChatReq(messages=[msg0, msg1])

    resp: ChatRes = await get_openai().chat(chat_req=params)

    assert "assistant" == resp.choices[0].message.role
    assert "Newton" in resp.choices[0].message.content
