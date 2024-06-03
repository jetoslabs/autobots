from typing import List

from loguru import logger
from openai import AsyncOpenAI
from openai._base_client import AsyncPaginator
from openai.pagination import AsyncCursorPage
from openai.types.beta.vector_stores import VectorStoreFileBatch, VectorStoreFile

from src.autobots.conn.openai.openai_vector_stores.openai_vector_store_file_batches.openai_vector_store_file_batches_model import \
    CreateVectorStoreFileBatch, ListVectorStoreFilesInBatch, RetrieveVectorStoreFileBatch, CancelVectorStoreFileBatch


class OpenaiVectorStoreFileBatches:

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

    async def create(self, create_vector_store_file_batch: CreateVectorStoreFileBatch) -> VectorStoreFileBatch:
        try:
            vector_store_file_batch = await self.client.beta.vector_stores.file_batches.create(
                **create_vector_store_file_batch.model_dump(exclude_none=True)
            )
            return vector_store_file_batch
        except Exception as e:
            logger.error(str(e))
            raise

    async def list(self, list_vector_store_files_in_batch: ListVectorStoreFilesInBatch) -> List[VectorStoreFile]:
        try:
            vector_store_files_cursor: AsyncPaginator[VectorStoreFile, AsyncCursorPage[VectorStoreFile]] \
                = await self.client.beta.vector_stores.file_batches.list_files(
                    **list_vector_store_files_in_batch.model_dump(exclude_none=True)
                )
            vector_store_files = []
            async for vector_store_file in vector_store_files_cursor:
                if len(vector_store_files) >= list_vector_store_files_in_batch.limit:
                    break
                vector_store_files.append(vector_store_file)
            return vector_store_files
        except Exception as e:
            logger.error(str(e))
            raise

    async def retrieve(self, retrieve_vector_store_file_batch: RetrieveVectorStoreFileBatch) -> VectorStoreFileBatch:
        try:
            cancel_vector_store_file_batch = await self.client.beta.vector_stores.file_batches.retrieve(
                **retrieve_vector_store_file_batch.model_dump(exclude_none=True)
            )
            return cancel_vector_store_file_batch
        except Exception as e:
            logger.error(str(e))
            raise

    async def cancel(self, cancel_vector_store_file_batch: CancelVectorStoreFileBatch) -> VectorStoreFileBatch:
        try:
            cancel_vector_store_file_batch = await self.client.beta.vector_stores.file_batches.cancel(
                **cancel_vector_store_file_batch.model_dump(exclude_none=True)
            )
            return cancel_vector_store_file_batch
        except Exception as e:
            logger.error(str(e))
            raise
