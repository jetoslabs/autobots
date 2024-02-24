import pytest

from src.autobots.action.action.common_action_models import TextObj
from src.autobots.action.action_type.action_text2text.action_text2text_user_input import ActionText2textUserInput


@pytest.mark.asyncio
async def test_action_text2text_user_input_happy_path(set_test_settings):
    action_config = TextObj(text="action_config")
    action = ActionText2textUserInput(action_config=action_config)

    action_input = TextObj(text="action_input")
    action_output = await action.run_action(action_input)

    assert len(action_output.texts) == 2
    assert action_output.texts[0].text == "action_config"
    assert action_output.texts[1].text == "action_input"


@pytest.mark.asyncio
async def test_action_text2text_user_input_empty_config_happy_path(set_test_settings):
    action_config = TextObj(text="")
    action = ActionText2textUserInput(action_config=action_config)

    action_input = TextObj(text="action_input")
    action_output = await action.run_action(action_input)

    assert len(action_output.texts) == 1
