import datetime

import pytest
from openai._base_client import HttpxBinaryResponseContent

from autobots.conn.openai.openai_client import get_openai
from autobots.conn.openai.speech_model import SpeechReq


@pytest.mark.asyncio
async def test_chat_happy_path(set_test_settings):
    params = SpeechReq(
        input=f"Hello! I am Autobots X. I am here to assist you. Today is {datetime.datetime.now().date()}. "
    )

    resp:  HttpxBinaryResponseContent = await get_openai().speech(speech_req=params)
    resp.stream_to_file(f"./tests/resources/test.{params.response_format}")
    assert resp is not None
