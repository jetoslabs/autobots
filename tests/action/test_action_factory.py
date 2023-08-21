
import pytest
import pytest_asyncio
from pydantic import HttpUrl

from autobots.action.action_factory import ActionFactory
from autobots.action.llm_chat import LLMChat, LLMChatData
from autobots.action.read_urls import ReadUrls, ReadUrlsData
from autobots.conn.openai.chat import ChatReq, Message
from autobots.core.settings import get_settings


# Run command `python -m pytest -s` from `autobots/tests` folder
@pytest_asyncio.fixture
async def set_settings():
    settings = get_settings(_env_file='../.env.local')


@pytest.mark.skip(reason="Selenium driver not working")
@pytest.mark.asyncio
async def test_action_factory_read_urls_happy_path(set_settings):
    name = "read_urls"
    factory = ActionFactory()
    await factory.register(name, ReadUrls, ReadUrlsData)
    action_class, action_data_class = await factory.get_action_classes(name)

    action_data = action_data_class(name=name, read_urls_req=[HttpUrl("https://meetkiwi.co")])
    action_data = await factory.run_action(action_class(), action_data)
    assert len(action_data.context) > 0
    assert True


@pytest.mark.asyncio
async def test_action_factory_llm_chat_happy_path(set_settings):
    name = "llm_chat"
    factory = ActionFactory()
    await factory.register(name, LLMChat, LLMChatData)
    action_class, action_data_class = await factory.get_action_classes(name)

    msg0 = Message(role="system", content="You are a helpful assistant.")
    msg1 = Message(role="user", content="What structure of a good blog")
    chat_req = ChatReq(messages=[msg0, msg1])

    action_data = action_data_class(name=name, chat_req=chat_req)
    action_data = await factory.run_action(action_class(), action_data)
    assert len(action_data.context) > 0
    assert True


