from functools import lru_cache

from autobots.conn.aws.s3 import S3, get_s3
from autobots.conn.pinecone.pinecone import Pinecone, get_pinecone
from autobots.core.settings import Settings, get_settings
from autobots.datastore.datastore import Datastore


class DatastoreFactory:

    def __init__(self, s3: S3 = get_s3(), pinecone: Pinecone = get_pinecone()):
        # s3 conn
        self.s3 = s3
        # pinecone conn
        self.pinecone = pinecone

    async def list_datastore(self):
        datastore_s3 = await self.s3.list("")
        return datastore_s3

    async def create_datastore(self, name: str) -> Datastore:
        datastore = Datastore(s3=self.s3, pinecone=self.pinecone).init(name=name)
        return datastore

    async def hydrate_datastore(self, datastore_id: str) -> Datastore:
        datastore = Datastore(s3=self.s3, pinecone=self.pinecone).hydrate(datastore_id=datastore_id)
        return datastore


@lru_cache
def get_datastore_factory(settings: Settings = get_settings()) -> DatastoreFactory:
    return DatastoreFactory()
