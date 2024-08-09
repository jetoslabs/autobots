import pytest

from src.autobots.action.action.action_doc_model import ActionDoc
from src.autobots.action.action_type.action_factory import ActionFactory
from src.autobots.action.action_type.action_map import ACTION_MAP
from src.autobots.action.action_type.action_text2text.action_text2text_read_api_file import ActionText2textReadApiFile, ActionConfig, ActionInput
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.data_model.context import Context
import asyncio

@pytest.mark.asyncio
async def test_action_text2text_api_1_happy_path(set_test_settings):
    action_config = ActionConfig(text="Github")
    action = ActionText2textReadApiFile(action_config)
    action_input = ActionInput(text="Github")
    action_output = await action.run_action(Context(),action_input)
