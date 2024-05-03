from loguru import logger
from openai import AsyncOpenAI
from openai._base_client import AsyncPaginator
from openai.pagination import AsyncCursorPage
from openai.types.beta import Assistant, AssistantDeleted

from src.autobots.conn.openai.openai_assistants.assistant_model import AssistantCreate, AssistantRetrieve, \
    AssistantList, \
    AssistantDelete, AssistantUpdate
from src.autobots.conn.openai.openai_assistants.openai_threads.openai_threads import OpenaiThreads


class OpenaiAssistants():

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        self.threads = OpenaiThreads(openai_client)

    async def create(self, assistant_create: AssistantCreate) -> Assistant | None:
        try:
            assistant = await self.client.beta.assistants.create(**assistant_create.model_dump(exclude_none=True))
            return assistant
        except Exception as e:
            logger.error(str(e))
            raise

    async def retrieve(self, assistant_retrieve: AssistantRetrieve) -> Assistant | None:
        try:
            return await self.client.beta.assistants.retrieve(**assistant_retrieve.model_dump(exclude_unset=True))
        except Exception as e:
            logger.error(str(e))
            raise

    async def list(self, assistant_list: AssistantList) -> AsyncPaginator[Assistant, AsyncCursorPage[Assistant]]:
        try:
            return await self.client.beta.assistants.list(**assistant_list.model_dump(exclude_none=True))
        except Exception as e:
            logger.error(str(e))
            raise

    async def delete(self, assistant_delete: AssistantDelete) -> AssistantDeleted | None:
        try:
            return await self.client.beta.assistants.delete(**assistant_delete.model_dump(exclude_none=True))
        except Exception as e:
            logger.error(str(e))
            raise

    async def update(self, assistant_update: AssistantUpdate) -> Assistant | None:
        try:
            return await self.client.beta.assistants.update(**assistant_update.model_dump(exclude_none=True))
        except Exception as e:
            logger.error(str(e))
            raise
