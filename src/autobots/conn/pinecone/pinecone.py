import time
from functools import lru_cache
from typing import List

from loguru import logger
from pinecone import Index, QueryResponse, FetchResponse, PodSpec
import pinecone as pc
from retry import retry

from src.autobots.conn.openai.openai_embeddings.embedding_model import EmbeddingReq, EmbeddingRes
from src.autobots.conn.openai.openai_client import OpenAI, get_openai
from src.autobots.core.settings import Settings, SettingsProvider


class Pinecone:

    def __init__(
            self,
            api_key: str,
            environment: str,
            open_ai: OpenAI = get_openai(),
            index_name: str = "index-1536",
            dimension: int = 1536,
    ):
        if not api_key or not environment:
            return
        self.open_ai = open_ai
        self.pinecone = pc.Pinecone(api_key=api_key, region=environment, project_id="fa82a0e")
        self.spec = PodSpec(environment=environment)
        self.index_name = index_name
        self.dimension = dimension
        self.index = self.create_index()

    def create_index(self) -> Index:
        """
        Only create index if it doesn't exist
        :return:
        """

        if self.index_name not in self.pinecone.list_indexes().names():
            self.pinecone.create_index(name=self.index_name, dimension=self.dimension, spec=self.spec)
            time.sleep(3)
        index = self.pinecone.Index(self.index_name)
        return index

    @retry(exceptions=Exception, tries=5, delay=30)
    async def upsert_data(self, vector_id: str, data: str, metadata: dict, namespace: str = "default"):
        try:
            upserted = []
            embedding_req = EmbeddingReq(input=data)
            embedding_res: EmbeddingRes = await self.open_ai.openai_embeddings.embeddings(embedding_req)
            for embedding_data in embedding_res.data:
                # vector = (Vector_ID, Dense_vector_values, Vector_metadata)
                vector = (vector_id, embedding_data.embedding, metadata)
                upsert_res = self.index.upsert(vectors=[vector], namespace=namespace)
                upserted.append(upsert_res)
        except Exception as e:
            logger.error(str(e))
            raise

    async def query(
            self,
            data: str,
            namespace: str = "default",
            top_k: int = 10,
            filter: dict = None,
            include_values: bool = True,
            include_metadata: bool = True,
    ) -> QueryResponse:
        embedding_req = EmbeddingReq(input=data)
        embedding_res: EmbeddingRes = await self.open_ai.openai_embeddings.embeddings(embedding_req)
        try:
            for embedding_data in embedding_res.data:
                res: QueryResponse = self.index.query(
                    vector=embedding_data.embedding,
                    namespace=namespace,
                    top_k=top_k,
                    filter=filter,
                    include_values=include_values,
                    include_metadata=include_metadata
                )
                return res
        except Exception as e:
            logger.error(str(e))

    async def fetch(self, vector_ids: List[str], namespace: str = "default") -> FetchResponse:
        fetch_res = self.index.fetch(ids=vector_ids, namespace=namespace)
        return fetch_res

    async def delete_all(self, namespace: str | None = None):
        deleted = self.index.delete(delete_all=True, namespace=namespace)
        return deleted

    async def delete_metadata(
            self,
            filter: dict[str, str | float | int | bool | list | dict] | None = None,
            namespace: str | None = None
    ) -> dict:
        deleted = self.index.delete(filter=filter, namespace=namespace)
        return deleted


@lru_cache
def get_pinecone(settings: Settings = SettingsProvider.sget()) -> Pinecone:
    return Pinecone(api_key=settings.PINECONE_API_KEY, environment=settings.PINECONE_ENVIRONMENT)
