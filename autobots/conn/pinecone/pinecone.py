import time
from typing import List, Any

import pinecone
from pinecone import QueryResponse, FetchResponse, ScoredVector

from autobots.conn.openai.embedding import EmbeddingReq, EmbeddingRes
from autobots.conn.openai.openai import OpenAI
from autobots.core.settings import get_settings


class Pinecone:

    def __init__(
            self,
            open_ai: OpenAI,
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
            upsert_res = self.index.upsert(vectors=[vector], namespace="default")
            upserted.append(upsert_res)

    async def query(
            self,
            query: str,
            namespace: str = "default",
            top_k: int = 10,
            include_values: bool = True,
            include_metadata: bool = True,
            filter: dict = None
    ) -> List[ScoredVector]:
        embedding_req = EmbeddingReq(input=query)
        embedding_res: EmbeddingRes = await self.open_ai.embedding(embedding_req)
        for embedding_data in embedding_res.data:
            res: QueryResponse = self.index.query(embedding_data.embedding, top_k=top_k, namespace=namespace)
            return res.get("matches")

    async def fetch(self, vector_ids: List[str], namespace: str = "default") -> FetchResponse:
        fetch_res: FetchResponse = self.index.fetch(ids=vector_ids, namespace=namespace)
        return fetch_res
