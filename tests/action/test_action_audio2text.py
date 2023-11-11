import pytest

from autobots.action.action_type.action_audio2text.action_audio2text_openai import AudioRes, ActionAudio2TextOpenai
from autobots.conn.openai.transcription_model import TranscriptionReq


@pytest.mark.asyncio
async def test_speech_happy_path(set_test_settings):
    config = TranscriptionReq()
    input = AudioRes(url="https://cdn.openai.com/API/docs/audio/alloy.wav")
    transcription = await ActionAudio2TextOpenai(action_config=config).run_action(input)
    assert transcription and transcription.text != ""
