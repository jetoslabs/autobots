import pytest
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionToolParam

from src.autobots.action.action.action_doc_model import ActionDoc
from src.autobots.action.action_type.action_factory import ActionFactory
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.openai.openai_chat.chat_model import ChatReq
from langjam.openai.openai_function.openai_function import OpenaiFunction

@pytest.mark.asyncio
async def test_action_text2text_llm_chat_openai_rerun_happy_path(set_test_settings):
    action_config = ChatReq(
        messages=[
            ChatCompletionUserMessageParam(
                role="user",
                content="Write a simple story"
            )
        ],
        model="gpt-4-0613"
    )
    action_doc = ActionDoc(
        id="action_doc_1",
        user_id="user_id_1",
        name="action_1",
        type=ActionType.text2text_llm_chat_openai,
        config=action_config.model_dump(exclude_none=True)
    )
    action_input = {"text": "Sunny day in Sahara"}
    action_run_obj_1 = await ActionFactory.run_action(action_doc, action_input)
    assert action_run_obj_1.output_dict
    assert len(action_run_obj_1.config_dict.get("messages")) == 1

    action_doc.config = action_run_obj_1.config_dict
    action_doc.input = action_run_obj_1.input_dict
    action_doc.output = action_run_obj_1.output_dict

    action_input = {"text": "Keep the same plot but make it funny"}
    action_run_obj_2 = await ActionFactory.run_action(action_doc, action_input)
    assert action_run_obj_2.output_dict
    assert len(action_run_obj_2.config_dict.get("messages")) == 3
    assert action_run_obj_2.config_dict.get("messages")[1].get("content") == action_run_obj_1.input_dict.get("text")
    assert action_run_obj_1.output_dict.get("texts")[0].get("text") in action_run_obj_2.config_dict.get("messages")[2].get("content")

serp_function =  {
        "name": "get_local_ads",
        "description": "Get local ads from google serp api",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Query to pass in serp local ads api"
                },
                "location": {
                    "type": "string",
                    "description": "location to pass in serp local ads api for which we need locals ads for"
                }
            },
            "required": ["location","query"]
        }
}

@pytest.mark.asyncio
async def test_action_text2text_llm_chat_openai_with_serp_function_rerun_happy_path(set_test_settings):
    action_config = ChatReq(
        messages=[
            ChatCompletionUserMessageParam(
                role="user",
                content="I am passing a serp api function in chat api tools. Suggest to call it if i ask any relevant question."
            )
        ],
        model="gpt-4-0613",
        tools= [
            ChatCompletionToolParam(
                function = serp_function,
                type = "function"
            )
        ]
    )
    action_doc = ActionDoc(
        id="action_doc_1",
        user_id="user_id_1",
        name="action_1",
        type=ActionType.text2text_llm_chat_openai,
        config=action_config.model_dump(exclude_none=True)
    )
    action_input = {"text": "What is local ads market for coffee in new delhi"}
    action_run_obj_1 = await ActionFactory.run_action(action_doc, action_input)
    assert action_run_obj_1.output_dict
    assert len(action_run_obj_1.config_dict.get("messages")) == 1


serp_function_organic_results =  {
        "name": "get_organic_results",
        "description": "Get organic results from google serp api for a product",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Query to pass in serp organic results api"
                },
                "location": {
                    "type": "string",
                    "description": "location to pass in serp organic results  for which we need organic results for"
                }
            },
            "required": ["location","query"]
        }
}

@pytest.mark.asyncio
async def test_action_text2text_llm_chat_openai_with_serp_function_rerun_happy_path(set_test_settings):
    action_config = ChatReq(
        messages=[
            ChatCompletionUserMessageParam(
                role="user",
                content="I am passing a serp api function in chat api tools. Suggest to call it if i ask any relevant question."
            )
        ],
        model="gpt-4-0613",
        tools= [
            ChatCompletionToolParam(
                function = serp_function_organic_results,
                type = "function"
            )
        ]
    )
    action_doc = ActionDoc(
        id="action_doc_1",
        user_id="user_id_1",
        name="action_1",
        type=ActionType.text2text_llm_chat_openai,
        config=action_config.model_dump(exclude_none=True)
    )
    action_input = {"text": "What is organic results for coffee in new delhi"}
    action_run_obj_1 = await ActionFactory.run_action(action_doc, action_input)
    assert action_run_obj_1.output_dict
    assert len(action_run_obj_1.config_dict.get("messages")) == 1

