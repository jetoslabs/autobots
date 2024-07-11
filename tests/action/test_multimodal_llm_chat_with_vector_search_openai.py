import base64
import io
import re
import uuid
from PIL import Image
import os
import pytest
import asyncio
from src.autobots.conn.chroma.chroma import Chroma, Document
from src.autobots.conn.chroma.multi_vector import MultiVectorRetriever, BaseStore
from src.autobots.conn.openai.openai_embeddings.openai_embeddings import OpenaiEmbeddings
from src.autobots.datastore.data_provider import DataProvider
from src.autobots.action.action.action_doc_model import ActionDoc, ActionResult
from src.autobots.action.action_type.action_factory import ActionFactory
from src.autobots.action.action_type.action_text2text.action_multimodal_llm_chat_with_vector_search_openai import \
    ActionCreateMultiModalLlmChatWithVectorSearchOpenaiConfig
from src.autobots.datastore.multidatastore import MultiDataStore
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.openai.openai_chat.chat_model import ChatReq
from openai.types.chat import ChatCompletionUserMessageParam

@pytest.mark.asyncio
async def test_action_multimodal_llm_chat_with_vector_search_openai_rerun_happy_path():
    query = "Give me company names that are interesting investments based on EV / NTM and NTM rev growth. Consider EV / NTM multiples vs historical?"
    global datastore
    datastore =  MultiDataStore(file_name="tests/resources/datastore/cj/cj.pdf",id="name")
    retriever = await datastore.init()
    chat_req = ChatReq(
        messages=[
            ChatCompletionUserMessageParam(
                role="user",
                content="Write a simple story"
            )
        ],
        model="gpt-4-0613"
    )
    action_config = ActionCreateMultiModalLlmChatWithVectorSearchOpenaiConfig(
        datastore_id=datastore.id,
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
    action_run_obj_1 = await ActionFactory.run_action(action_doc, action_input)
    print(action_run_obj_1)
    # On Action run: for every run we add context input

asyncio.run(test_action_multimodal_llm_chat_with_vector_search_openai_rerun_happy_path())