from typing import List

from fastapi import HTTPException
from pymongo.database import Database
from pymongo.results import DeleteResult

from autobots.conn.aws.s3 import S3, get_s3
from autobots.conn.pinecone.pinecone import Pinecone, get_pinecone
from autobots.datastore.datastore_meta_crud import DatastoreMetaCRUD
from autobots.datastore.datastore import Datastore
from autobots.datastore.datastore_meta_doc_model import DatastoreMetaDocCreate, DatastoreMetaDoc, DatastoreMetaDocFind
from autobots.user.user_orm_model import UserORM


class UserDatastore(Datastore):

    def __init__(self, user: UserORM, db: Database, s3: S3 = get_s3(), pinecone: Pinecone = get_pinecone()):
        super().__init__(s3, pinecone)
        self.user = user
        self.db = db
        self.datastore_meta_crud = DatastoreMetaCRUD(self.db)

    async def init(self, name: str) -> DatastoreMetaDoc:
        super().init(name)
        datastore_meta_doc_create = DatastoreMetaDocCreate(user_id=str(self.user.id), datastore_id=self.id, name=self.name)
        user_datastore_meta = await self.datastore_meta_crud.insert_one(datastore_meta_doc_create)
        return user_datastore_meta

    async def hydrate(self, datastore_id: str) -> Datastore:
        datastore_meta_doc_find = DatastoreMetaDocFind(user_id=str(self.user.id), datastore_id=datastore_id)
        datastore_metas = await self.datastore_meta_crud.find(datastore_meta_doc_find)
        if len(datastore_metas) != 1:
            raise HTTPException(405, "Datastore not found")
        datastore_meta = datastore_metas[0]
        datastore = super().hydrate(datastore_meta.datastore_id)
        return datastore

    async def get(self, name: str) -> DatastoreMetaDoc:
        datastore_meta_doc_find = DatastoreMetaDocFind(user_id=str(self.user.id), name=name)
        datastore_metas = await self.datastore_meta_crud.find(datastore_meta_doc_find)
        if len(datastore_metas) != 1:
            raise HTTPException(405, "Datastore not found")
        return datastore_metas[0]

    async def get_by_datastore_id(self, datastore_id: str) -> DatastoreMetaDoc:
        datastore_meta_doc_find = DatastoreMetaDocFind(user_id=str(self.user.id), datastore_id=datastore_id)
        datastore_metas = await self.datastore_meta_crud.find(datastore_meta_doc_find)
        if len(datastore_metas) != 1:
            raise HTTPException(405, "Datastore not found")
        return datastore_metas[0]

    async def list(self, limit: int = 100, offset: int = 0) -> List[DatastoreMetaDoc]:
        datastore_meta_doc_find = DatastoreMetaDocFind(user_id=str(self.user.id))
        datastore_metas = await self.datastore_meta_crud.find(datastore_meta_doc_find, limit, offset)
        return datastore_metas

    async def delete(self, datastore_id: str) -> DeleteResult:
        # delete s3 and pinecone entries
        user_datastore = await self.hydrate(datastore_id)
        await user_datastore.empty_and_close()
        # delete meta entry
        datastore_meta_doc_find = DatastoreMetaDocFind(user_id=str(self.user.id), datastore_id=datastore_id)
        deleted_result = await self.datastore_meta_crud.delete_many(datastore_meta_doc_find)
        return deleted_result
