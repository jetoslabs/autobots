import datetime

import pytest

from autobots.action.action.common_action_models import TextObj
from autobots.action.action_type.action_text2audio.action_text2audio_openai import ActionText2AudioOpenai
from autobots.conn.openai.speech_model import SpeechReq


@pytest.mark.asyncio
async def test_speech_happy_path(set_test_settings):
    config = SpeechReq(
        input=f"Hello! I am Autobot X. I am here to assist you.",
    )
    input = TextObj(text=f"Today is {datetime.datetime.now().strftime('%B %d, %Y')}.")
    url = await ActionText2AudioOpenai(action_config=config).run_action(input)
    assert url and url != ""
