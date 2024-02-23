from loguru import logger
from openai import AsyncOpenAI
from openai.types.beta import Thread
from openai.types.beta.threads import Run

from src.autobots.conn.openai.openai_assistants.openai_thread_messages.openai_thread_messages import OpenaiThreadMessages
from src.autobots.conn.openai.openai_assistants.openai_thread_runs.openai_thread_runs import OpenaiThreadRuns
from src.autobots.conn.openai.openai_assistants.openai_threads.openai_threads_model import ThreadCreate, ThreadRetrieve, \
    ThreadUpdate, ThreadDelete, ThreadCreateAndRun


class OpenaiThreads():

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        self.messages = OpenaiThreadMessages(openai_client)
        self.runs = OpenaiThreadRuns(openai_client)

    async def create_and_run(self, thread_create_and_run: ThreadCreateAndRun) -> Run:
        try:
            run = await self.client.beta.threads.create_and_run(**thread_create_and_run.model_dump(exclude_none=True))
            return run
        except Exception as e:
            logger.error(str(e))

    async def create(self, thread_create: ThreadCreate) -> Thread:
        try:
            return await self.client.beta.threads.create(**thread_create.model_dump(exclude_none=True))
        except Exception as e:
            logger.error(str(e))

    async def retrieve(self, thread_retrieve: ThreadRetrieve) -> Thread:
        try:
            return await self.client.beta.threads.retrieve(**thread_retrieve.model_dump(exclude_none=True))
        except Exception as e:
            logger.error(str(e))

    async def update(self, thread_update: ThreadUpdate):
        try:
            return await self.client.beta.threads.update(**thread_update.model_dump(exclude_none=True))
        except Exception as e:
            logger.error(str(e))

    async def delete(self, thread_delete: ThreadDelete):
        try:
            return await self.client.beta.threads.delete(**thread_delete.model_dump(exclude_none=True))
        except Exception as e:
            logger.error(str(e))
