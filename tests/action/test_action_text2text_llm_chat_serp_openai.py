import pytest
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionToolParam

from src.autobots.action.action.action_doc_model import ActionDoc
from src.autobots.action.action_type.action_factory import ActionFactory
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.openai.openai_chat.chat_model import ChatReq
from langjam.openai.openai_function.openai_function import OpenaiFunction

from src.autobots.conn.serp.serp_ads.serp_ads import get_local_ads
from src.autobots.function.function_map import FUNCTION_MAP

serp_function =  {
        "name": "get_local_ads",
        "description": "Get local serp_ads from google serp api",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Query to pass in serp local serp_ads api"
                },
                "location": {
                    "type": "string",
                    "description": "location to pass in serp local serp_ads api for which we need locals serp_ads for"
                }
            },
            "required": ["location","query"]
        }
}

@pytest.mark.asyncio
async def test_action_text2text_llm_chat_openai_with_serp_ads_function_rerun_happy_path(set_test_settings):
    defination = await OpenaiFunction.get_defination(get_local_ads, "this function gets local serp_ads from google serp" +
                                                            " api")
    action_config = ChatReq(
        messages=[
            ChatCompletionUserMessageParam(
                role="user",
                content="I am passing a serp api function in chat api tools. Suggest to call it if i ask any relevant question."
            )
        ],
        model="gpt-4-0613",
        tools= [
            defination
            # ChatCompletionToolParam(
            #     function = serp_function,
            #     type = "function"
            # )
        ]
    )
    action_doc = ActionDoc(
        id="action_doc_1",
        user_id="user_id_1",
        name="action_1",
        type=ActionType.text2text_llm_chat_openai,
        config=action_config.model_dump(exclude_none=True)
    )
    action_input = {"text": "What is local serp_ads market for coffee in new delhi"}
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
async def test_action_text2text_llm_chat_openai_with_serp_organic_results_function_rerun_happy_path(set_test_settings):
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

serp_function_shopping_results = {
        "name": "get_shopping_results",
        "description": "Get shopping results from google serp api for a product",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Query to pass in serp shopping results api"
                }
            },
            "required": ["query"]
        }
}

@pytest.mark.asyncio
async def test_action_text2text_llm_chat_openai_with_serp_shopping_results_function_rerun_happy_path(set_test_settings):
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
                function = serp_function_shopping_results,
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
    action_input = {"text": "What is shopping results for coffee in new delhi"}
    action_run_obj_1 = await ActionFactory.run_action(action_doc, action_input)
    assert action_run_obj_1.output_dict
    assert len(action_run_obj_1.config_dict.get("messages")) == 1


