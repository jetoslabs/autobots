import pytest

from src.autobots.action.action.common_action_models import TextObj
from src.autobots.action.action_type.action_multimodal.action_multimodal_assistant_openai.action_multimodal_assistant_openai import \
    ActionMultimodalAssistantOpenai
from src.autobots.action.action_type.action_multimodal.action_multimodal_assistant_openai.assistant_openai_model import \
    AssistantOpenaiConfigCreate


@pytest.mark.asyncio
async def test_action_multimodal_assistant_openai_happy_path(set_test_settings):
    action: ActionMultimodalAssistantOpenai | None = None
    try:
        action_config_create = AssistantOpenaiConfigCreate(
            name="test_action_multimodal_assistant_openai_happy_path",
            tools=[
                {
                    "type": "code_interpreter"
                },
                "google_search",
            ],
            tool_resources={
                "code_interpreter": {
                    "file_ids": ["file-bnPln9tOtw1R249D2mU4Td6C"]
                }
            }
        )
        action_config = await ActionMultimodalAssistantOpenai.create_config(action_config_create)
        action = ActionMultimodalAssistantOpenai(action_config)
        action_input = TextObj(
            text="Find me the latest news of India. Then analyze the sentiment of the news you told me and create bar chart of news count vs sentiment")
        action_output = await action.run_action(action_input)
        assert "India" in action_output.texts[0].text
    finally:
        if action:
            await ActionMultimodalAssistantOpenai.delete_config(action.action_config)

