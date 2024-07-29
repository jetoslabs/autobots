import pytest

from src.autobots.action.action.action_doc_model import ActionDoc, ActionResult
from src.autobots.action.action_type.action_factory import ActionFactory
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.claude.chat_model import ChatReqClaude, Message
from src.autobots.data_model.context import Context
from src.autobots.llm.tools.tool_factory_claude import ToolFactoryClaude

@pytest.mark.asyncio
async def test_action_text2text_llm_chat_claude_rerun_happy_path():
    tools = await ToolFactoryClaude.get_tools()
    assert tools is not None
    tool_defs = await ToolFactoryClaude.get_tool_definations(tools)
    assert tool_defs is not None


    action_config = ChatReqClaude(
        messages=[
            Message(role="user", content="Be a helpful assistant")
        ],
        model="claude-3-5-sonnet-20240620",
        tools=tools
    )
    action_doc = ActionDoc(
        id="action_doc_1",
        user_id="user_id_1",
        name="action_1",
        type=ActionType.text2text_llm_chat_claude,
        config=action_config.model_dump(exclude_none=True)
    )
    action_input = {"text": "Summarize latest new of India"}
    # action_input = {"text": "Learn about Meetkiwi and Research competitors of Meetkiwi"}
    action_run_obj_1 = await ActionFactory.run_action(Context(), action_doc, action_input)
    assert action_run_obj_1.output_dict
    # assert len(action_run_obj_1.config_dict.get("messages")) > 1

    action_doc.config = action_run_obj_1.config_dict
    action_doc.input = action_run_obj_1.input_dict
    action_doc.output = action_run_obj_1.output_dict
    action_doc.results.append(ActionResult(input=action_doc.input, output=action_doc.output))

    action_input = {"text": "Keep the same plot but make it funny"}
    action_run_obj_2 = await ActionFactory.run_action(Context(), action_doc, action_input)
    assert action_run_obj_2.output_dict
    # assert len(action_run_obj_2.config_dict.get("messages")) > 3
    # assert action_run_obj_2.config_dict.get("messages")[1].get("content") == action_run_obj_1.input_dict.get("text")
    # assert action_run_obj_1.output_dict.get("texts")[0].get("text") in action_run_obj_2.config_dict.get("messages")[-2].get("content")