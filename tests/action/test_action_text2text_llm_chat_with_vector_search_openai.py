import pytest
from openai.types.chat import ChatCompletionUserMessageParam

from src.autobots.action.action.action_doc_model import ActionDoc
from src.autobots.action.action_type.action_factory import ActionFactory
from src.autobots.action.action_type.action_text2text.action_text2text_llm_chat_with_vector_search_openai import \
    ActionCreateText2TextLlmChatWithVectorSearchOpenaiConfig
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.aws.s3 import get_s3
from src.autobots.conn.openai.openai_chat.chat_model import ChatReq
from src.autobots.conn.pinecone.pinecone import get_pinecone
from src.autobots.conn.unstructured_io.unstructured_io import get_unstructured_io
from src.autobots.datastore.datastore import Datastore

text = ("## Definition of story structure"
        "\n# As the sequence and backbone of your book, story structure is the order in which you present the narrative. The linear storyline shapes the flow of events (rising action, climax, and resolution) while establishing the book’s setting and plot."
        "\n# Before we get into the different story archetypes and narrative types, there are a few fundamental structural elements worth learning. While these are most often used to describe written storytelling, you can easily use this structure to push a visually-driven story along. They include:"
        "\n# Opener"
        "\nThe opener establishes your story’s setting, premise, plot, and character roles. A compelling opener teases readers with what challenges or conflicts are ahead."
        "\n# Incident"
        "\nStage two is the story’s incident. As the catalyst or instigating force that compels your main character to act, the incident establishes the conflict that sets the stage for the third phase of a story’s structure."
        "\n# Crisis"
        "\nAs a consequence of the incident, the story’s crisis is an unfolding of the primary conflict or series of issues. A crisis must be realistic and related to the plot. If the character experiences more than one crisis, each should build on the last, heightening the sense of danger and tension."
        "\n# Climax"
        "\nStage four is the climax or the height of the crisis. Depending on your perspective, you can also think of the climax as the bottom of your action. At this stage, the character has hit rock bottom in the storyline–hopeless and seemingly out of options. The climax is not the end of the book but the beginning of the end."
        "\n# Ending"
        "\nThe final stage of the story structure is the ending or close. Success or failure are both valid outcomes, but the ending should provide a conclusion and resolution to your story. The ending should close the loop on all crises, plot twists, and loose ends but could also leave the reader wanting more. "
        )

@pytest.mark.asyncio
async def test_action_text2text_llm_chat_with_vector_search_openai_rerun_happy_path(set_test_settings):
    global datastore
    try:
        chat_req = ChatReq(
            messages=[
                ChatCompletionUserMessageParam(
                    role="user",
                    content="Write a simple story"
                )
            ],
            model="gpt-4-0613"
        )

        s3 = get_s3()
        pinecone = get_pinecone()
        unstructured = get_unstructured_io()
        datastore = Datastore(s3, pinecone, unstructured).init(name="vector_search_teststore")
        await datastore.put_data(text)

        action_config = ActionCreateText2TextLlmChatWithVectorSearchOpenaiConfig(
            datastore_id=datastore.id,
            chat_req=chat_req
        )
        action_doc = ActionDoc(
            id="action_doc_1",
            user_id="user_id_1",
            name="action_1",
            type=ActionType.text2text_llm_chat_with_vector_search_openai,
            config=action_config.model_dump(exclude_none=True)
        )
        action_input = {"text": "Sunny day in Sahara"}
        action_run_obj_1 = await ActionFactory.run_action(action_doc, action_input)
        # On Action run: for every run we add context input
        assert action_run_obj_1.output_dict
        assert len(action_run_obj_1.config_dict.get("chat_req").get("messages")) == 2

        action_doc.config = action_run_obj_1.config_dict
        action_doc.input = action_run_obj_1.input_dict
        action_doc.output = action_run_obj_1.output_dict

        action_input = {"text": "Keep the same plot but make it funny"}
        action_run_obj_2 = await ActionFactory.run_action(action_doc, action_input)
        # On Action run: for every run we add context input
        assert action_run_obj_2.output_dict
        assert len(action_run_obj_2.config_dict.get("chat_req").get("messages")) == 5
        #
        assert (action_run_obj_2.config_dict.get("chat_req").get("messages")[2].get("content") ==
                action_run_obj_1.input_dict.get("text"))
        assert action_run_obj_1.output_dict.get("texts")[0].get("text") in action_run_obj_2.config_dict.get("chat_req").get("messages")[
            3].get("content")
    finally:
        await datastore.empty_and_close()

