import pytest
import pytest_asyncio

from autobots.action.llm_chat import LLMChatData, LLMChat
from autobots.action.prompt.blog_writer import blog_writer_messages
from autobots.conn.openai.chat import Role, Message, ChatReq
from autobots.core.settings import get_settings


# Run command `pytest -vv -n 5` from `autobots/tests` folder
@pytest_asyncio.fixture
async def set_settings():
    settings = get_settings(_env_file='../.env.local')


@pytest.mark.asyncio
async def test_blog_writer_happy_path(set_settings):
    usr_msg = Message(role=Role.user, content="Blog topic is Role of ethics in Artificial Intelligence")
    chat_req = ChatReq(messages=blog_writer_messages+[usr_msg])

    llm_chat_data = LLMChatData(name="test_chat", chat_req=chat_req)
    await LLMChat().run(llm_chat_data)

    assert llm_chat_data.context[-1].role == "assistant"
