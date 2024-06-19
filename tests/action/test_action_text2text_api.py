import pytest

from src.autobots.action.action_type.action_text2text.action_text2text_api import APIRequest, ActionText2textAPI, \
    APIInput


@pytest.mark.asyncio
async def test_action_text2text_api_1_happy_path(set_test_settings):
    action_config = APIRequest(
        method="GET",
        url="https://api.adviceslip.com/advice",
        headers={"Content-Type": "application/json"}
    )
    action = ActionText2textAPI(action_config)
    action_input = APIInput()
    action_output = await action.run_action(action_input)
    assert action_output.status_code == 200
    assert action_output.text.__contains__("slip")
