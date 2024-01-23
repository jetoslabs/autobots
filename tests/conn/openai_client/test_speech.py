import datetime
import io

import pytest
from openai._legacy_response import HttpxBinaryResponseContent

from autobots.conn.aws.aws_s3 import get_public_s3
from autobots.conn.openai.openai_client import get_openai
from autobots.conn.openai.openai_audio.speech_model import SpeechReq
from autobots.core.utils import gen_hash


@pytest.mark.asyncio
async def test_speech_happy_path(set_test_settings):
    input = f"Hello! I am Autobot X. I am here to assist you. Today is {datetime.datetime.now().strftime('%B %d, %Y')}."
    params = SpeechReq(
        input=input
    )
    resp:  HttpxBinaryResponseContent = await get_openai().openai_audio.speech(speech_req=params)
    assert resp is not None

    url = await get_public_s3().put_file_obj(
        io.BytesIO(resp.content),
        f"{gen_hash(input)}.{params.response_format}"
    )
    assert url != ""

    # resp.stream_to_file(f"./tests/resources/test.{params.response_format}")

