from loguru import logger
from openai import AsyncOpenAI
from openai._base_client import AsyncPaginator
from openai.pagination import AsyncCursorPage
from openai.types.beta import Assistant, AssistantDeleted
from openai.types.beta.assistants import AssistantFile, FileDeleteResponse


from src.autobots.conn.openai.openai_assistants.assistant_model import (
    AssistantCreate,
    AssistantRetrieve,
    AssistantList,
    AssistantDelete,
    AssistantUpdate,
    AssistantFileInput,
    AssistantFileListInput,
)
from src.autobots.conn.openai.openai_assistants.openai_threads.openai_threads import (
    OpenaiThreads,
)


class OpenaiAssistants:
    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client
        self.threads = OpenaiThreads(openai_client)

    async def create(self, assistant_create: AssistantCreate) -> Assistant | None:
        try:
            return await self.client.beta.assistants.create(
                **assistant_create.model_dump(exclude_none=True)
            )
        except Exception as e:
            logger.error(str(e))

    async def retrieve(self, assistant_retrieve: AssistantRetrieve) -> Assistant | None:
        try:
            return await self.client.beta.assistants.retrieve(
                **assistant_retrieve.model_dump(exclude_unset=True)
            )
        except Exception as e:
            logger.error(str(e))

    async def list(
        self, assistant_list: AssistantList
    ) -> AsyncPaginator[Assistant, AsyncCursorPage[Assistant]]:
        try:
            return await self.client.beta.assistants.list(
                **assistant_list.model_dump(exclude_none=True)
            )
        except Exception as e:
            logger.error(str(e))

    async def delete(
        self, assistant_delete: AssistantDelete
    ) -> AssistantDeleted | None:
        try:
            return await self.client.beta.assistants.delete(
                **assistant_delete.model_dump(exclude_none=True)
            )
        except Exception as e:
            logger.error(str(e))

    async def update(self, assistant_update: AssistantUpdate) -> Assistant | None:
        try:
            return await self.client.beta.assistants.update(
                **assistant_update.model_dump(exclude_none=True)
            )
        except Exception as e:
            logger.error(str(e))

    async def create_file(
        self, assistant_file_input: AssistantFileInput
    ) -> AssistantFile | None:
        try:
            return await self.client.beta.assistants.files.create(
                **assistant_file_input.model_dump(exclude_none=True)
            )
        except Exception as e:
            logger.error(str(e))

    async def retrieve_file(
        self, assistant_file_input: AssistantFileInput
    ) -> AssistantFile | None:
        try:
            return await self.client.beta.assistants.files.retrieve(
                **assistant_file_input.model_dump(exclude_none=True)
            )
        except Exception as e:
            logger.error(str(e))

    async def delete_file(
        self, assistant_file_input: AssistantFileInput
    ) -> FileDeleteResponse | None:
        try:
            return await self.client.beta.assistants.files.delete(
                **assistant_file_input.model_dump(exclude_none=True)
            )
        except Exception as e:
            logger.error(str(e))

    async def list_files(
        self, assistant_file_input: AssistantFileListInput
    ) -> AsyncPaginator[AssistantFile, AsyncCursorPage[AssistantFile]] | None:
        try:
            return await self.client.beta.assistants.files.list(
                **assistant_file_input.model_dump(exclude_none=True)
            )
        except Exception as e:
            logger.error(str(e))
