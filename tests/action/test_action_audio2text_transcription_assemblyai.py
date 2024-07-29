import pytest

from src.autobots.action.action_type.action_audio2text.action_audio2text_transcription_assemblyai import AudioUrl, \
    ActionAudio2TextTranscriptionAssemblyai
from src.autobots.conn.assembly.assemblyai import TranscriptionReq

from src.autobots.action.action.action_doc_model import ActionDoc
from src.autobots.action.action_type.action_factory import ActionFactory, RunActionObj

from src.autobots.data_model.context import Context

@pytest.mark.skip("Not successful")
@pytest.mark.asyncio
async def test_action_audio2text_transcription_assemblyai_happy_path(set_test_settings):
    config = TranscriptionReq()
    input = AudioUrl(text="https://meetkiwiinc.zendesk.com/attachments/token/DV6HIgMxsVG8rINvioXo6u0ZW/?name=recording+316829.mp3")
    # transcription = await ActionAudio2TextTranscriptionAssemblyai(action_config=config).run_action(input)
    action_doc = ActionDoc(
        id="1",
        user_id="user_1",
        name="Action_for_celery",
        type=ActionAudio2TextTranscriptionAssemblyai.type,
        config=config.model_dump(exclude_none=True),
    )
    run_action_object: RunActionObj = await ActionFactory.run_action(
        Context(),
        action_doc,
        input.model_dump(exclude_none=True)
    )
    action_output = ActionAudio2TextTranscriptionAssemblyai.get_output_type().model_validate(
        run_action_object.output_dict
    )
    assert action_output
    # assert transcription.text!=""