import pytest
import pytest_asyncio

from autobots.action.llm_chat import LLMChatData, LLMChat
from autobots.conn.openai.chat import Message, ChatReq
from autobots.core.settings import get_settings


# Run command `python -m pytest -s` from `autobots/tests` folder
@pytest_asyncio.fixture
async def set_settings():
    settings = get_settings(_env_file='../.env.local')


@pytest.mark.asyncio
async def test_llm_chat_happy_path(set_settings):
    msg0 = Message(role="system", content="You are a helpful assistant.")
    msg1 = Message(role="user", content="What structure of a good blog")
    chat_req = ChatReq(messages=[msg0, msg1])

    llm_chat_data = LLMChatData(name="test_chat", chat_req=chat_req)
    await LLMChat().run(llm_chat_data)

    assert llm_chat_data.context[-1].role == "assistant"
