from loguru import logger
from openai import AsyncOpenAI
from openai._base_client import AsyncPaginator
from openai.pagination import AsyncCursorPage
from openai.types.beta import VectorStore, VectorStoreDeleted

from src.autobots.conn.openai.openai_vector_stores.openai_vector_stores.openai_vector_stores_model import \
    CreateVectorStore, ListVectorStore, RetrieveVectorStore, UpdateVectorStore, DeleteVectorStore


class OpenaiVectorStores:

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

    async def create(self, create_vector_store: CreateVectorStore) -> VectorStore:
        try:
            vector_store = await self.client.beta.vector_stores.create(
                **create_vector_store.model_dump(exclude_none=True)
            )
            return vector_store
        except Exception as e:
            logger.error(str(e))
            raise

    async def list(self, list_vector_store: ListVectorStore) -> AsyncPaginator[VectorStore, AsyncCursorPage[VectorStore]]:
        try:
            vector_store = await self.client.beta.vector_stores.list(
                **list_vector_store.model_dump(exclude_none=True)
            )
            return vector_store
        except Exception as e:
            logger.error(str(e))
            raise

    async def retrieve(self, retrieve_vector_store: RetrieveVectorStore) -> VectorStore:
        try:
            vector_store = await self.client.beta.vector_stores.retrieve(
                **retrieve_vector_store.model_dump(exclude_none=True)
            )
            return vector_store
        except Exception as e:
            logger.error(str(e))
            raise

    async def update(self, update_vector_store: UpdateVectorStore) -> VectorStore:
        try:
            vector_store = await self.client.beta.vector_stores.update(
                **update_vector_store.model_dump(exclude_none=True)
            )
            return vector_store
        except Exception as e:
            logger.error(str(e))
            raise

    async def delete(self, delete_vector_store: DeleteVectorStore) -> VectorStoreDeleted:
        try:
            vector_store = await self.client.beta.vector_stores.delete(
                **delete_vector_store.model_dump(exclude_none=True)
            )
            return vector_store
        except Exception as e:
            logger.error(str(e))
            raise
