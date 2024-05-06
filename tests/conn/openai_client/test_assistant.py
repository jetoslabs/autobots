import time

import pytest
from openai.types.beta import CodeInterpreterToolParam, FileSearchToolParam

from src.autobots.conn.openai.openai_assistants.assistant_model import AssistantCreate, AssistantDelete

from src.autobots.conn.openai.openai_assistants.openai_thread_messages.openai_thread_messages_model import \
    ThreadMessagesCreate, ThreadMessageList
from src.autobots.conn.openai.openai_assistants.openai_thread_runs.openai_thread_runs_model import ThreadRunCreate, \
    ThreadRunRetrieve
from src.autobots.conn.openai.openai_assistants.openai_threads.openai_threads_model import ThreadCreate, ThreadDelete
from src.autobots.conn.openai.openai_client import get_openai


@pytest.mark.asyncio
async def test_assistant_happy_path(set_test_settings):
    assistant_client = get_openai().openai_assistants
    global_assistant_id = ""
    global_thread_id = ""
    try:
        """ create action """
        # create assistant
        assistant_create = AssistantCreate(
            name="test_assistant",
            model="gpt-4-turbo-preview",
            instructions="Generate sql query only",
            # file_ids=["file-5h9P25H5PEVXYGdPzdKs4Rpb"],
            tools=[
                CodeInterpreterToolParam(type="code_interpreter"),
                FileSearchToolParam(type="file_search")
            ]
        )
        assistant = await assistant_client.create(assistant_create)
        global_assistant_id = assistant.id

        """ run action (input: messages) """
        # create thread
        thread_create = ThreadCreate()
        thread = await assistant_client.threads.create(thread_create)
        global_thread_id = thread.id
        # add message
        thread_message_create_1 = ThreadMessagesCreate(thread_id=thread.id, content="who has the highest number of blogs")
        thread_message = await assistant_client.threads.messages.create(thread_message_create_1) # noqa F841
        # run thread
        tools = [tool.model_dump() for tool in assistant.tools]
        thread_run_create = ThreadRunCreate(thread_id=thread.id, assistant_id=assistant.id, instructions=assistant.instructions, tools=tools)
        run = await assistant_client.threads.runs.create(thread_run_create)
        # # create thread and run
        # tools = [tool.model_dump() for tool in assistant.tools]
        # thread_run_and_create = ThreadCreateAndRun(assistant_id=assistant.id, instructions=assistant.instructions, tools=tools)
        # run = await assistant_client.threads.create_and_run(thread_run_and_create)
        # get run status - loop until status completed
        thread_run_retrieve = ThreadRunRetrieve(thread_id=run.thread_id, run_id=run.id)
        run_retrieved = await assistant_client.threads.runs.retrieve(thread_run_retrieve)
        while run_retrieved.status in ["queued", "in_progress", "cancelling"]:
            time.sleep(10)
            run_retrieved = await assistant_client.threads.runs.retrieve(thread_run_retrieve)
        # get list of messages
        if run_retrieved.status != "completed":
            assert False
        thread_message_list = ThreadMessageList(thread_id=run_retrieved.thread_id)
        messages = await assistant_client.threads.messages.list(thread_message_list)
        assert len(messages.data) >= 2
    except Exception:
        assert False
    finally:
        # delete thread
        thread_delete = ThreadDelete(thread_id=global_thread_id)
        await assistant_client.threads.delete(thread_delete)
        # delete assistant
        assistant_delete = AssistantDelete(assistant_id=global_assistant_id)
        await assistant_client.delete(assistant_delete)



