import pytest as pytest
from openai import AsyncStream
from openai.types.chat import ChatCompletion, ChatCompletionUserMessageParam, ChatCompletionSystemMessageParam, \
    ChatCompletionChunk

from autobots.conn.openai.chat import ChatReq
from autobots.conn.openai.openai_client import get_openai


@pytest.mark.asyncio
async def test_chat_happy_path(set_test_settings):
    msg0 = ChatCompletionSystemMessageParam(role="system", content="You are a helpful assistant.")
    msg1 = ChatCompletionUserMessageParam(role="user", content="Most famous Mechanics law")
    params = ChatReq(messages=[msg0, msg1], model="gpt-3.5-turbo-16k-0613")

    resp: ChatCompletion = await get_openai().chat(chat_req=params)

    assert "assistant" == resp.choices[0].message.role
    assert "Newton" in resp.choices[0].message.content


@pytest.mark.asyncio
async def test_chat_stream_happy_path(set_test_settings):
    msg0 = ChatCompletionSystemMessageParam(role="system", content="You are a helpful assistant.")
    msg1 = ChatCompletionUserMessageParam(role="user", content="Most famous Mechanics law")
    params = ChatReq(messages=[msg0, msg1], model="gpt-3.5-turbo-16k-0613", stream=True)

    stream = await get_openai().chat(chat_req=params)

    collected_words = ""
    async for part in stream:
        assert part.object == "chat.completion.chunk"
        if part.choices[0].delta.content:
            collected_words = collected_words + part.choices[0].delta.content.lower()

    assert "newton" in collected_words
