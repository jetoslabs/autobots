from autobots.conn.aws.s3 import S3, get_s3
from autobots.conn.pinecone.pinecone import Pinecone, get_pinecone
from autobots.database.database_models import UserORM, DatastoreMetaORM
from autobots.database.datastore_meta_crud import DatastoreMetaCRUD
from autobots.datastore.datastore import Datastore


class UserDatastore(Datastore):

    def __init__(self, user: UserORM, s3: S3 = get_s3(), pinecone: Pinecone = get_pinecone()):
        super().__init__(s3, pinecone)
        self.user = user

    def init(self, name: str):
        super().init(name)
        datastore_meta = DatastoreMetaORM(user_id=self.user.id, name=self.name, id=self.id)
        await DatastoreMetaCRUD.create(datastore_meta)
        return self

    def hydrate(self, name: str):
        datastore_metas = await DatastoreMetaCRUD.read(self.user.id, name)
        datastore_meta = datastore_metas[0]
        super().hydrate(datastore_meta.id)
        return self
