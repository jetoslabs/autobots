import pytest

from autobots.action.action_type.action_audio2text.action_audio2text_transcription_openai import AudioRes, ActionAudio2TextTranscriptionOpenai
from autobots.conn.openai.openai_audio.transcription_model import TranscriptionReq


@pytest.mark.asyncio
async def test_action_audio2text_transcription_openai_happy_path(set_test_settings):
    config = TranscriptionReq()
    input = AudioRes(url="https://cdn.openai.com/API/docs/audio/alloy.wav")
    transcription = await ActionAudio2TextTranscriptionOpenai(action_config=config).run_action(input)
    assert transcription and transcription.text != ""
