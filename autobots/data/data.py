import random
import string
from typing import List

from pinecone import ScoredVector

from autobots.conn.aws.s3 import S3, get_s3
from autobots.conn.pinecone.pinecone import Pinecone, get_pinecone
from autobots.core.utils import gen_filename


class Datastore:
    """
    DataStore will store data s3 and embedding in pinecone
    Each datastore will have unique path in S3 to store data
    Each datastore will have unique namespace in pinecone
    """

    def __init__(self, name: str, s3: S3 = get_s3(), pinecone: Pinecone = get_pinecone()):
        self.name = name
        self.trace = ''.join(random.choices(string.hexdigits, k=9))
        # Id for the datastore is unique identifier for the datastore
        self.id = f"{self.name}-{self.trace}"
        # s3 conn
        self.s3 = s3
        # pinecone conn
        self.pinecone = pinecone

    def _get_s3_basepath(self):
        return self.id

    def _get_namespace(self):
        return self.id

    async def _put_data(self, data: str):
        await self.s3.put(data=data, filename=f"{self._get_s3_basepath()}/{gen_filename(data)}")

    async def _put_embedding(self, data: str):
        await self.pinecone.upsert_data(
            gen_filename(data),
            data=data, metadata={},
            namespace=self._get_namespace()
        )

    async def put(self, data: str):
        """
        Store data
        :return:
        """
        await self._put_data(data=data)
        await self._put_embedding(data=data)

    async def get(self):
        """
        Retrieve data
        :return:
        """
        pass

    async def search(self, query: str) -> List[str]:
        """
        Semantic search data
        :return:
        """
        result = []
        scored_vectors: List[ScoredVector] = await self.pinecone.query(data=query, namespace=self._get_namespace())
        for scored_vector in scored_vectors:
            data = await self.s3.get(f"{self._get_s3_basepath()}/{scored_vector.id}")
            result.append(data)
        return result

