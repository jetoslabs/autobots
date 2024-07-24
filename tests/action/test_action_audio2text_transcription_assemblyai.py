import pytest

from src.autobots.action.action_type.action_audio2text.action_audio2text_transcription_assemblyai import AudioRes, AudioUrl, \
    ActionAudio2TextTranscriptionAssemblyai
from src.autobots.conn.assembly.assemblyai import TranscriptionReq
import asyncio

@pytest.mark.asyncio
async def test_action_audio2text_transcription_assemblyai_happy_path(set_test_settings):
    config = TranscriptionReq()
    input = AudioUrl(url="https://meetkiwiinc.zendesk.com/attachments/token/DV6HIgMxsVG8rINvioXo6u0ZW/?name=recording+316829.mp3")
    transcription = await ActionAudio2TextTranscriptionAssemblyai(action_config=config).run_action(input)
    assert transcription.text!=""
