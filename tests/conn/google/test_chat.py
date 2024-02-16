import pytest as pytest
from google.generativeai.types import ContentDict

from src.autobots.conn.google.google_genai_chat.chat_model import ChatReq
from src.autobots.conn.google.google_genai_client import get_google_genai


@pytest.mark.asyncio
async def test_chat_happy_path(set_test_settings):
    msg0 = ContentDict(role="user", parts=["Most famous Mechanics law"])
    params = ChatReq(contents=[msg0])

    resp = await get_google_genai().google_genai_chat.chat(chat_req=params)

    async for part in resp:
        # This will only loop once in this test since stream is by default set to
        # False in params above

        role = part.candidates[0].content.role
        assert "model" == role, part
        assert "Newton" in part.text, part
