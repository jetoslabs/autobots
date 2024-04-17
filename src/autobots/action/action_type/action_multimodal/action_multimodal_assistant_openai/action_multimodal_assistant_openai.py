import time
from typing import Type, List

from loguru import logger

from src.autobots.action.action.common_action_models import TextObj, TextObjs
from src.autobots.action.action_type.abc.IAction import IAction, ActionInputType, ActionOutputType, ActionConfigType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_multimodal.action_multimodal_assistant_openai.assistant_openai_model import \
    AssistantOpenaiConfigCreate, AssistantOpenaiConfigUpdate, AssistantOpenaiConfig
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.openai.openai_assistants.assistant_model import AssistantDelete, AssistantUpdate
from src.autobots.conn.openai.openai_assistants.openai_thread_messages.openai_thread_messages_model import \
    ThreadMessagesCreate, ThreadMessageList
from src.autobots.conn.openai.openai_assistants.openai_thread_runs.openai_thread_runs_model import ThreadRunCreate, \
    ThreadRunRetrieve
from src.autobots.conn.openai.openai_assistants.openai_threads.openai_threads_model import ThreadCreate
from src.autobots.conn.openai.openai_client import get_openai


class ActionMultimodalAssistantOpenai(
    IAction[AssistantOpenaiConfigCreate, AssistantOpenaiConfigUpdate, AssistantOpenaiConfig, TextObj, TextObjs]
):
    type = ActionType.multimodal_assistant_openai

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return AssistantOpenaiConfigCreate

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return AssistantOpenaiConfigUpdate

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return AssistantOpenaiConfig

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return TextObj

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return TextObjs

    @staticmethod
    async def create_config(config_create: AssistantOpenaiConfigCreate) -> AssistantOpenaiConfig:
        assistant_client = get_openai().openai_assistants
        # create assistant
        assistant: AssistantOpenaiConfig = await assistant_client.create(config_create)
        return assistant

    @staticmethod
    async def update_config(config: AssistantOpenaiConfig, config_update: AssistantOpenaiConfigUpdate) -> AssistantOpenaiConfig:
        assistant_client = get_openai().openai_assistants
        assistant_update = AssistantUpdate(assistant_id=config.id, **config_update.model_dump(exclude_none=True))
        assistant = await assistant_client.update(assistant_update)
        return assistant

    @staticmethod
    async def delete_config(config: AssistantOpenaiConfig) -> AssistantOpenaiConfig:
        assistant_client = get_openai().openai_assistants
        # delete assistant
        assistant_delete = AssistantDelete(assistant_id=config.id)
        await assistant_client.delete(assistant_delete)
        return config

    async def run_action(self, action_input: TextObj) -> TextObjs:
        assistant_client = get_openai().openai_assistants
        assistant = self.action_config
        try:
            # create thread
            thread_create = ThreadCreate()
            thread = await assistant_client.threads.create(thread_create)
            # add message
            thread_message_create_1 = ThreadMessagesCreate(thread_id=thread.id,
                                                           content=action_input.text)
            thread_message = await assistant_client.threads.messages.create(thread_message_create_1)  # noqa F841
            # run thread
            tools = [tool.model_dump() for tool in assistant.tools]
            thread_run_create = ThreadRunCreate(thread_id=thread.id, assistant_id=assistant.id,
                                                instructions=assistant.instructions, tools=tools)
            run = await assistant_client.threads.runs.create(thread_run_create)
            # get run status - loop until status completed
            thread_run_retrieve = ThreadRunRetrieve(thread_id=run.thread_id, run_id=run.id)
            run_retrieved = await assistant_client.threads.runs.retrieve(thread_run_retrieve)
            while run_retrieved.status in ["queued", "in_progress", "cancelling"]:
                time.sleep(10)
                run_retrieved = await assistant_client.threads.runs.retrieve(thread_run_retrieve)
            # get list of messages
            if run_retrieved.status != "completed":
                raise Exception(f"Assistant run status: {run_retrieved.status}")
            thread_message_list = ThreadMessageList(thread_id=run_retrieved.thread_id)
            messages = await assistant_client.threads.messages.list(thread_message_list)
            # create return object
            message = messages.data[0]  # last generated message is on the top
            texts: List[TextObj] = []
            for content in message.content:
                text_obj = TextObj(text=content.text.value)
                texts.append(text_obj)
            return TextObjs(texts=texts)
        except Exception as e:
            logger.error(str(e))
            raise e
