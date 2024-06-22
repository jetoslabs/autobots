import pytest


from src.autobots.action.action_type.action_video2video.action_video2video_opus import ActionVideo2VideoOpus, Video2VideoRunModel
from src.autobots.conn.opus.opus import Video2VideoReqModel
from src.autobots.action.action.action_doc_model import ActionDoc
from src.autobots.action.action_type.action_factory import ActionFactory, RunActionObj


@pytest.mark.asyncio
async def test_action_video2video_opus_happy_path(set_test_settings):
    
    action_config = Video2VideoReqModel()
    action_input = Video2VideoRunModel(
       url = "https://www.youtube.com/watch?v=nJN_tHjzT9I"
    )
    action_doc = ActionDoc(
        id="1",
        user_id="user_1",
        name="Action_for_celery",
        type=ActionVideo2VideoOpus.type,
        config=action_config.model_dump(exclude_none=True),
    )
    run_action_object: RunActionObj = await ActionFactory.run_action(
        action_doc,
        action_input.model_dump(exclude_none=True)
    )
    action_output = ActionVideo2VideoOpus.get_output_type().model_validate(
        run_action_object.output_dict
    )
    assert action_output.url is not None
