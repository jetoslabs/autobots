import pytest

from src.autobots.action.action_type.action_audio2text.action_audio2text_transcription_assemblyai import AudioRes, \
    ActionAudio2TextTranscriptionAssemblyai
from src.autobots.conn.openai.openai_audio.transcription_model import TranscriptionReq

@pytest.mark.asyncio
async def test_action_audio2text_transcription_assemblyai_happy_path(set_test_settings):
    config = TranscriptionReq()
    input = AudioRes(url="https://meetkiwiinc.zendesk.com/attachments/token/DV6HIgMxsVG8rINvioXo6u0ZW/?name=recording+316829.mp3")
    transcription = await ActionAudio2TextTranscriptionAssemblyai(action_config=config).run_action(input)
    assert transcription and transcription.text != ""
