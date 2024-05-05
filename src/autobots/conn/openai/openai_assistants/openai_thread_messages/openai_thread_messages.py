from loguru import logger
from openai import AsyncOpenAI
from openai._base_client import AsyncPaginator
from openai.pagination import AsyncCursorPage
from openai.types.beta.threads import Message

from src.autobots.conn.openai.openai_assistants.openai_thread_messages.openai_thread_messages_model import \
    ThreadMessagesCreate, ThreadMessagesRetrieve, ThreadMessageUpdate, ThreadMessageList


class OpenaiThreadMessages():

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

    async def create(self, thread_messages_create: ThreadMessagesCreate) -> Message | None:
        try:
            return await self.client.beta.threads.messages.create(
                **thread_messages_create.model_dump(exclude_none=True))
        except Exception as e:
            logger.error(str(e))
            raise

    async def retrieve(self, thread_messages_retrieve: ThreadMessagesRetrieve) -> Message | None:
        try:
            return await self.client.beta.threads.messages.retrieve(
                **thread_messages_retrieve.model_dump(exclude_none=True))
        except Exception as e:
            logger.error(str(e))
            raise

    async def update(self, thread_messages_update: ThreadMessageUpdate) -> Message | None:
        try:
            return await self.client.beta.threads.messages.update(
                **thread_messages_update.model_dump(exclude_none=True))
        except Exception as e:
            logger.error(str(e))
            raise

    async def list(self, thread_messages_list: ThreadMessageList) -> AsyncPaginator[Message, AsyncCursorPage[Message]]:
        try:
            return await self.client.beta.threads.messages.list(
                **thread_messages_list.model_dump(exclude_none=True))
        except Exception as e:
            logger.error(str(e))
            raise
