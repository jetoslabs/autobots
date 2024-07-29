import pytest

from src.autobots.action.action.action_doc_model import ActionDoc
from src.autobots.action.action_type.action_factory import ActionFactory
from src.autobots.action.action_type.action_map import ACTION_MAP
from src.autobots.action.action_type.action_text2text.action_text2text_api import APIRequest, ActionText2textAPI, \
    APIInput
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.data_model.context import Context


@pytest.mark.asyncio
async def test_action_text2text_api_1_happy_path(set_test_settings):
    action_config = APIRequest(
        method="GET",
        url="https://api.adviceslip.com/advice",
        headers={"Content-Type": "application/json"}
    )
    action = ActionText2textAPI(action_config)
    action_input = APIInput()
    action_output = await action.run_action(Context(),action_input)
    assert action_output.status_code == 200
    assert action_output.content.__contains__("slip")


@pytest.mark.asyncio
async def test_action_text2text_api_2_happy_path(set_test_settings):
    action_type = ActionType.text2text_api_call
    action = ACTION_MAP.get(action_type)
    action_input_dict = {
        "method": "GET",
        "url": "https://api.adviceslip.com/advice",
        "headers": {"Content-Type": "application/json"}
    }
    action.get_input_type().model_validate(action_input_dict)
    action_doc = ActionDoc(
        id="id_test_action_text2text_api_1_happy_path",
        user_id="user_test_action_text2text_api_1_happy_path",
        name="name_test_action_text2text_api_1_happy_path",
        type=action_type,
        config=action_input_dict,
    )
    run_action_obj = await ActionFactory.run_action(Context(), action_doc, action_input_dict)
    run_output = action.get_output_type().model_validate(run_action_obj.output_dict)
    assert run_output.status_code == 200
    assert run_output.content.__contains__("slip")


@pytest.mark.skip("For now")
@pytest.mark.asyncio
async def test_action_text2text_api_slack_post_message_happy_path(set_test_settings):
    action_type = ActionType.text2text_api_call
    action = ACTION_MAP.get(action_type)
    action_input_dict = {
        "method": "POST",
        "url": "https://slack.com/api/chat.postMessage",
        "headers": {
            # "Content-Type": "application/json; charset=utf-8",
            "Authorization": "Bearer xoxb-abc"
        },
        "body": {
            "channel": "C07BRNL20CA",
            "text": "Hello world :tada:"
        },
    }
    action.get_input_type().model_validate(action_input_dict)
    action_doc = ActionDoc(
        id="id_test_action_text2text_api_slack_post_message_happy_path",
        user_id="user_test_action_text2text_api_slack_post_message_happy_path",
        name="name_test_action_text2text_api_slack_post_message_happy_path",
        type=action_type,
        config=action_input_dict,
    )
    run_action_obj = await ActionFactory.run_action(Context(), action_doc, {})
    run_output = action.get_output_type().model_validate(run_action_obj.output_dict)
    assert run_output.status_code == 200
    assert run_output.text.__contains__("\"ok\":true")
