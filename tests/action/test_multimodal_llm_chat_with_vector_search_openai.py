import pytest
from src.autobots.data_model.context import Context
from src.autobots.action.action.action_doc_model import ActionDoc
from src.autobots.action.action_type.action_factory import ActionFactory
from src.autobots.action.action_type.action_text2text.action_multimodal_llm_chat_with_vector_search_openai import \
    ActionCreateMultiModalLlmChatWithVectorSearchOpenaiConfig
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.openai.openai_chat.chat_model import ChatReq
from openai.types.chat import ChatCompletionUserMessageParam
import chromadb

@pytest.mark.asyncio
async def test_action_multimodal_llm_chat_with_vector_search_openai_rerun_happy_path(set_test_settings):
    query = "Give me company names that are interesting investments based on EV / NTM and NTM rev growth. Consider EV / NTM multiples vs historical?"
    global datastore
    # s3 = get_s3()
    settings = chromadb.config.Settings(is_persistent=True)
    settings.persist_directory='db'
#     client = chromadb.Client(settings)

# # Get all collections
#     collections = client.list_collections()

#     # Print all collection names
#     for collection in collections:
#         print(collection.id, collection.name)
  
    # datastore =  MultiDataStore(s3).init(id="vector_search_teststore")
    # await datastore.put_data(filename="tests/resources/datastore/cj/cj.pdf")
    chat_req = ChatReq(
        messages=[
            ChatCompletionUserMessageParam(
                role="user",
                content="Write a simple story"
            )
        ],
        model="gpt-4o-mini"
    )
    action_config = ActionCreateMultiModalLlmChatWithVectorSearchOpenaiConfig(
        datastore_id="vector_search_teststore-7fD7Eab3d",
        chat_req=chat_req
    )
    action_doc = ActionDoc(
        id="action_doc_1",
        user_id="user_id_1",
        name="action_1",
        type=ActionType.multimodal_llm_chat_with_vector_search_openai,
        config=action_config.model_dump(exclude_none=True)
    )
    action_input = {"text": query}
    action_run_obj_1 = await ActionFactory.run_action(Context(), action_doc, action_input)
    assert action_run_obj_1
    # On Action run: for every run we add context input
