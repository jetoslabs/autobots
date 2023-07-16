import time
from functools import lru_cache
from typing import List

import pinecone
from pinecone import QueryResponse, FetchResponse, ScoredVector
from pinecone.core.grpc.protos.vector_service_pb2 import DeleteResponse

from autobots.conn.openai.embedding import EmbeddingReq, EmbeddingRes
from autobots.conn.openai.openai import OpenAI, get_openai
from autobots.core.settings import get_settings, Settings


class Pinecone:

    def __init__(
            self,
            open_ai: OpenAI = get_openai(),
            index_name: str = "index-1536",
            dimension: int = 1536,
            api_key: str = get_settings().PINECONE_API_KEY,
            environment: str = get_settings().PINECONE_ENVIRONMENT
    ):
        self.open_ai = open_ai
        if not api_key or not environment:
            return
        pinecone.init(api_key=api_key, environment=environment)
        self.index_name = index_name
        self.dimension = dimension
        self.index = self.create_index()

    def create_index(self) -> pinecone.GRPCIndex:
        """
        Only create index if it doesn't exist
        :return:
        """
        if self.index_name not in pinecone.list_indexes():
            pinecone.create_index(name=self.index_name, dimension=self.dimension)
            time.sleep(3)
        index = pinecone.GRPCIndex(self.index_name)
        return index

    async def upsert_data(self, vector_id: str, data: str, metadata: dict, namespace: str = "default"):
        upserted = []
        embedding_req = EmbeddingReq(input=data)
        embedding_res: EmbeddingRes = await self.open_ai.embedding(embedding_req)
        for embedding_data in embedding_res.data:
            # vector = (Vector_ID, Dense_vector_values, Vector_metadata)
            vector = (vector_id, embedding_data.embedding, metadata)
            upsert_res = self.index.upsert(vectors=[vector], namespace=namespace)
            upserted.append(upsert_res)

    async def query(
            self,
            data: str,
            namespace: str = "default",
            top_k: int = 10,
            filter: dict = None,
            include_values: bool = None,
            include_metadata: bool = None,
    ) -> List[ScoredVector]:
        embedding_req = EmbeddingReq(input=data)
        embedding_res: EmbeddingRes = await self.open_ai.embedding(embedding_req)
        for embedding_data in embedding_res.data:
            res: QueryResponse = self.index.query(
                vector=embedding_data.embedding,
                namespace=namespace,
                top_k=top_k,
                filter=filter,
                include_values=include_values,
                include_metadata=include_metadata
            )
            return res.get("matches")

    async def fetch(self, vector_ids: List[str], namespace: str = "default") -> FetchResponse:
        fetch_res: FetchResponse = self.index.fetch(ids=vector_ids, namespace=namespace)
        return fetch_res

    async def delete(self,
                     ids:  list[str] | None = None,
                     delete_all: bool | None = None,
                     namespace: str | None = None,
                     filter: dict[str, str | float | int | bool | list | dict] | None = None
                     ) -> DeleteResponse:
        deleted = self.index.delete(ids=ids, delete_all=delete_all, namespace=namespace, filter=filter)
        return deleted


@lru_cache
def get_pinecone(settings: Settings = get_settings()) -> Pinecone:
    return Pinecone()
