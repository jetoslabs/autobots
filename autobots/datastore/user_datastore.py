from typing import List

from sqlalchemy.orm import Session

from autobots.conn.aws.s3 import S3, get_s3
from autobots.conn.pinecone.pinecone import Pinecone, get_pinecone
from autobots.datastore.datastore_meta_crud import DatastoreMetaCRUD
from autobots.datastore.datastore import Datastore
from autobots.datastore.datastore_meta_orm_model import DatastoreMetaORM
from autobots.user.user_orm_model import UserORM

# TODO: make Datastore a Field
class UserDatastore(Datastore):

    def __init__(self, user: UserORM, db: Session, s3: S3 = get_s3(), pinecone: Pinecone = get_pinecone()):
        super().__init__(s3, pinecone)
        self.user = user
        self.db = db

    async def init(self, name: str) -> DatastoreMetaORM:
        super().init(name)
        datastore_meta = DatastoreMetaORM(user_id=self.user.id, name=self.name, id=self.id)
        user_datastore_meta = await DatastoreMetaCRUD.create(datastore_meta, self.db)
        return user_datastore_meta

    async def hydrate(self, id: str) -> Datastore:
        datastore_meta = await DatastoreMetaCRUD.read_by_id(self.user.id, id, self.db)
        datastore = super().hydrate(datastore_meta.id)
        return datastore

    async def get(self, name: str) -> DatastoreMetaORM:
        user_datastore_meta = await DatastoreMetaCRUD.read_by_name_version(
            self.user.id, name, db=self.db
        )
        return user_datastore_meta[0]

    async def list(self, db: Session, limit: int = 100, offset: int = 0) -> List[DatastoreMetaORM]:
        user_datastore_metas = await DatastoreMetaCRUD.list(
            self.user.id, limit, offset, db=self.db
        )
        return user_datastore_metas

    async def delete(self, db: Session, id: str) -> DatastoreMetaORM:
        # delete s3 and pinecone entries
        user_datastore = await self.hydrate(id)
        await user_datastore.empty_and_close()
        # delete meta entry
        user_datastore_meta = await DatastoreMetaCRUD.read_by_id(self.user.id, id, self.db)
        deleted_meta = await DatastoreMetaCRUD.delete(user_datastore_meta, self.db)
        return deleted_meta
