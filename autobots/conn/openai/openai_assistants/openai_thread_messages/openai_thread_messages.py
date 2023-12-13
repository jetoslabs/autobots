from openai import AsyncOpenAI
from openai._base_client import AsyncPaginator
from openai.pagination import AsyncCursorPage
from openai.types.beta.threads import ThreadMessage
from openai.types.beta.threads.messages import MessageFile

from autobots.conn.openai.openai_assistants.openai_thread_messages.openai_thread_messages_model import \
    ThreadMessagesCreate, ThreadMessagesRetrieve, ThreadMessageUpdate, ThreadMessageList, ThreadMessageFileRetrieve, \
    ThreadMessageFileList
from autobots.core.logging.log import Log


class OpenaiThreadMessages():

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

    async def create(self, thread_messages_create: ThreadMessagesCreate) -> ThreadMessage | None:
        try:
            return await self.client.beta.threads.messages.create(
                **thread_messages_create.model_dump(exclude_none=True))
        except Exception as e:
            Log.error(str(e))

    async def retrieve(self, thread_messages_retrieve: ThreadMessagesRetrieve) -> ThreadMessage | None:
        try:
            return await self.client.beta.threads.messages.retrieve(
                **thread_messages_retrieve.model_dump(exclude_none=True))
        except Exception as e:
            Log.error(str(e))

    async def update(self, thread_messages_update: ThreadMessageUpdate) -> ThreadMessage | None:
        try:
            return await self.client.beta.threads.messages.update(
                **thread_messages_update.model_dump(exclude_none=True))
        except Exception as e:
            Log.error(str(e))

    async def list(self, thread_messages_list: ThreadMessageList) -> AsyncPaginator[ThreadMessage, AsyncCursorPage[ThreadMessage]]:
        try:
            return await self.client.beta.threads.messages.list(
                **thread_messages_list.model_dump(exclude_none=True))
        except Exception as e:
            Log.error(str(e))

    async def retrieve_message_file(self, thread_messages_file_retrieve: ThreadMessageFileRetrieve) -> MessageFile | None:
        try:
            return await self.client.beta.threads.messages.files.retrieve(
                **thread_messages_file_retrieve.model_dump(exclude_none=True))
        except Exception as e:
            Log.error(str(e))

    async def list_message_file(self, thread_messages_file_list: ThreadMessageFileList) -> AsyncPaginator[MessageFile, AsyncCursorPage[MessageFile]]:
        try:
            return await self.client.beta.threads.messages.files.list(
                **thread_messages_file_list.model_dump(exclude_none=True))
        except Exception as e:
            Log.error(str(e))
