import pytest as pytest
from langjam.openai.openai_function.openai_function import OpenaiFunction
from openai.types.chat import ChatCompletion, ChatCompletionUserMessageParam, ChatCompletionSystemMessageParam, \
    ChatCompletionToolParam

from src.autobots.conn.openai.openai_chat.chat_model import ChatReq
from src.autobots.conn.openai.openai_client import get_openai


@pytest.mark.asyncio
async def test_chat_happy_path(set_test_settings):
    msg0 = ChatCompletionSystemMessageParam(role="system", content="You are a helpful assistant.")
    msg1 = ChatCompletionUserMessageParam(role="user", content="Most famous Mechanics law")
    params = ChatReq(messages=[msg0, msg1], model="gpt-3.5-turbo-16k-0613")

    resp: ChatCompletion = await get_openai().openai_chat.chat(chat_req=params)

    assert "assistant" == resp.choices[0].message.role
    assert "Newton" in resp.choices[0].message.content


@pytest.mark.asyncio
async def test_vision_chat_happy_path(set_test_settings):
    msg0 = ChatCompletionSystemMessageParam(role="system", content="You are a helpful assistant.")
    msg1 = ChatCompletionUserMessageParam(role="user", content=[
          {
            "type": "text",
            "text": "What’s in this image?"
          },
          {
            "type": "image_url",
            "image_url": {
              "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
            }
          }
        ])
    params = ChatReq(messages=[msg0, msg1], model="gpt-4-vision-preview")

    resp: ChatCompletion = await get_openai().openai_chat.chat(chat_req=params)

    assert "assistant" == resp.choices[0].message.role
    assert "green" in resp.choices[0].message.content


@pytest.mark.asyncio
async def test_chat_stream_happy_path(set_test_settings):
    msg0 = ChatCompletionSystemMessageParam(role="system", content="You are a helpful assistant.")
    msg1 = ChatCompletionUserMessageParam(role="user", content="Most famous Mechanics law")
    params = ChatReq(messages=[msg0, msg1], model="gpt-3.5-turbo-16k-0613", stream=True)

    stream = await get_openai().openai_chat.chat(chat_req=params)

    collected_words = ""
    async for part in stream:
        assert part.object == "chat.completion.chunk"
        if part.choices[0].delta.content:
            collected_words = collected_words + part.choices[0].delta.content.lower()

    assert "newton" in collected_words


@pytest.mark.asyncio
async def test_openai_function(set_test_settings):
    chat_completion_tool_param: ChatCompletionToolParam = \
        await OpenaiFunction.get_defination(get_openai().openai_chat.chat, "LLM Chat")
    assert chat_completion_tool_param
