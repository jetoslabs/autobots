import datetime

import pytest

from src.autobots.action.action.common_action_models import TextObj
from src.autobots.action.action_type.action_text2audio.action_text2audio_speech_openai import ActionText2AudioSpeechOpenai
from src.autobots.conn.openai.openai_audio.speech_model import SpeechReq
from src.autobots.data_model.context import Context


@pytest.mark.asyncio
async def test_action_text2audio_speech_openai_happy_path(set_test_settings):
    config = SpeechReq(
        input="Hello! I am Autobot X. I am here to assist you.",
    )
    input = TextObj(text=f"Today is {datetime.datetime.now().strftime('%B %d, %Y')}.")
    audio_res = await ActionText2AudioSpeechOpenai(action_config=config).run_action(Context(), input)
    assert audio_res and audio_res.url != ""
