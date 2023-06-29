import pytest
import pytest_asyncio

from autobots.action.llm_chat import LLMChatData, LLMChat
from autobots.action.prompt.prompt_generator import prompt_generator_messages
from autobots.conn.openai.chat import Role, Message, ChatReq
from autobots.core.settings import get_settings


# Run command `pytest -vv -n 5` from `autobots/tests` folder
@pytest_asyncio.fixture
async def set_settings():
    settings = get_settings(_env_file='../.env.local')


@pytest.mark.asyncio
async def test_prompt_generator_for_blog_happy_path_1(set_settings):
    usr_msg = Message(role=Role.user, content="Travel to San Francisco blog.")
    chat_req = ChatReq(messages=prompt_generator_messages+[usr_msg])

    llm_chat_data = LLMChatData(name="test_chat", chat_req=chat_req)
    await LLMChat().run(llm_chat_data)

    assert llm_chat_data.context[-1].role == "assistant"

    blog_writer_messages = [
        Message(role=Role.user, content=llm_chat_data.context[-1].content)
    ]
    chat_req_1 = ChatReq(messages=blog_writer_messages)

    llm_chat_data_1 = LLMChatData(name="test_chat", chat_req=chat_req_1)
    await LLMChat().run(llm_chat_data_1)

    assert llm_chat_data_1.context[-1].role == "assistant"


@pytest.mark.asyncio
async def test_prompt_generator_for_python_happy_path_2(set_settings):
    usr_msg = Message(role=Role.user, content="Python code to google search latest weather of San Francisco.")
    chat_req = ChatReq(messages=prompt_generator_messages+[usr_msg])

    llm_chat_data = LLMChatData(name="test_chat", chat_req=chat_req)
    await LLMChat().run(llm_chat_data)

    assert llm_chat_data.context[-1].role == "assistant"

    python_code_messages = [
        Message(role=Role.user, content=f"\nOnly Output the python code for {llm_chat_data.context[-1].content}")
    ]
    chat_req_1 = ChatReq(messages=python_code_messages)

    llm_chat_data_1 = LLMChatData(name="test_chat", chat_req=chat_req_1)
    await LLMChat().run(llm_chat_data_1)

    assert llm_chat_data_1.context[-1].role == "assistant"
