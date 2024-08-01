import pytest

from src.autobots.action.action.common_action_models import TextObj, AssistantObj
from src.autobots.action.action_type.action_multimodal.action_multimodal_assistant_openai.action_multimodal_assistant_openai import \
    ActionMultimodalAssistantOpenai
from src.autobots.action.action_type.action_multimodal.action_multimodal_assistant_openai.assistant_openai_model import \
    AssistantOpenaiConfigCreate
from src.autobots.data_model.context import Context

@pytest.mark.asyncio
async def test_action_multimodal_assistant_openai_happy_path():
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
        action_input = AssistantObj(
            text="Explain the image", urls=["https://upload.wikimedia.org/wikipedia/en/9/9c/Archie_1942_issue_1.jpg"])
        action_output = await action.run_action(Context(), action_input)
        assert "India" in action_output.texts[0].text
    finally:
        if action:
            await ActionMultimodalAssistantOpenai.delete_config(action.action_config)

