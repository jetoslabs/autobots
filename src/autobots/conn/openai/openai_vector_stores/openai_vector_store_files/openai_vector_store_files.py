from loguru import logger
from openai import AsyncOpenAI
from openai._base_client import AsyncPaginator
from openai.pagination import AsyncCursorPage
from openai.types.beta.vector_stores import VectorStoreFile, VectorStoreFileDeleted

from src.autobots.conn.openai.openai_vector_stores.openai_vector_store_files.openai_vector_store_files_model import \
    CreateVectorStoreFile, ListVectorStoreFiles, RetrieveVectorStoreFile, DeleteVectorStoreFile


class OpenaiVectorStoreFiles:

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

    async def create(self, create_vector_store_file: CreateVectorStoreFile) -> VectorStoreFile:
        try:
            vector_store_file = await self.client.beta.vector_stores.files.create(
                **create_vector_store_file.model_dump(exclude_none=True)
            )
            return vector_store_file
        except Exception as e:
            logger.error(str(e))
            raise

    async def list(self, list_vector_store_files: ListVectorStoreFiles) -> AsyncPaginator[
        VectorStoreFile, AsyncCursorPage[VectorStoreFile]
    ]:
        try:
            vector_store_files = await self.client.beta.vector_stores.files.list(
                **list_vector_store_files.model_dump(exclude_none=True)
            )
            return vector_store_files
        except Exception as e:
            logger.error(str(e))
            raise

    async def retrieve(self, retrieve_vector_store_file: RetrieveVectorStoreFile) -> VectorStoreFile:
        try:
            vector_store_file = await self.client.beta.vector_stores.files.retrieve(
                **retrieve_vector_store_file.model_dump(exclude_none=True)
            )
            return vector_store_file
        except Exception as e:
            logger.error(str(e))
            raise

    async def delete(self, delete_vector_store_file: DeleteVectorStoreFile) -> VectorStoreFileDeleted:
        try:
            vector_store_file = await self.client.beta.vector_stores.files.delete(
                **delete_vector_store_file.model_dump(exclude_none=True)
            )
            return vector_store_file
        except Exception as e:
            logger.error(str(e))
            raise
