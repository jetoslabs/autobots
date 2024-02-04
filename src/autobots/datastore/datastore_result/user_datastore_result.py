from typing import List

from fastapi import HTTPException
from loguru import logger
from pymongo.database import Database

from src.autobots.datastore.datastore_result.datastore_result_doc_model import DatastoreResultCreate, DatastoreResultDoc, \
    DatastoreResultUpdate
from src.autobots.event_result.event_result_crud import EventResultCRUD
from src.autobots.event_result.event_result_model import EventResultDocCreate, EventResultFind, EventResultDocFind, \
    EventResultDocUpdate
from src.autobots.user.user_orm_model import UserORM


class UserDatastoreResult:

    def __init__(self, user: UserORM,  db: Database):
        self.user = user
        self.user_id = str(user.id)
        self.event_result_crud = EventResultCRUD(db)

    async def create_datastore_result(self, datastore_result:  DatastoreResultCreate) -> DatastoreResultDoc | None:
        try:
            event_result_doc_create = EventResultDocCreate(user_id=self.user_id, **datastore_result.model_dump())
            event_result_doc = await self.event_result_crud.insert_one(event_result_doc_create)
            datastore_result_doc = DatastoreResultDoc.model_validate(event_result_doc.model_dump())
            return datastore_result_doc
        except Exception as e:
            logger.error(str(e))
            raise e

    async def list_datastore_result(
            self, datastore_result_find: EventResultFind,
            limit: int = 100, offset: int = 0
    ) -> List[DatastoreResultDoc]:
        event_result_doc_find = EventResultDocFind(user_id=self.user_id, **datastore_result_find.model_dump())
        event_result_docs = await self.event_result_crud.find(event_result_doc_find, limit, offset)
        datastore_result_docs = []
        for event_result_doc in event_result_docs:
            datastore_result_doc = DatastoreResultDoc.model_validate(event_result_doc.model_dump())
            datastore_result_docs.append(datastore_result_doc)
        return datastore_result_docs

    async def get_datastore_result(
            self, datastore_result_id: str
    ) -> DatastoreResultDoc | None:
        try:
            event_result_doc_find = EventResultDocFind(id=datastore_result_id, user_id=self.user_id)
            event_result_docs = await self.event_result_crud.find(event_result_doc_find)
            if len(event_result_docs) != 1:
                raise HTTPException(500, "Error in finding result")
            event_result_doc = event_result_docs[0]
            datastore_result_doc = DatastoreResultDoc.model_validate(event_result_doc.model_dump())
            return datastore_result_doc
        except Exception as e:
            logger.error(str(e))
        return None

    async def update_datastore_result(
            self, datastore_result_id: str, datastore_update: DatastoreResultUpdate
    ) -> DatastoreResultDoc:
        try:
            event_result_doc_update = EventResultDocUpdate(id=datastore_result_id, user_id=self.user_id, **datastore_update.model_dump())
            event_result_doc = await self.event_result_crud.update_one(event_result_doc_update)
            datastore_result_doc = DatastoreResultDoc.model_validate(event_result_doc.model_dump())
            return datastore_result_doc
        except Exception as e:
            logger.error(str(e))
            raise e

    async def delete_datastore_result(
            self, id: str
    ) -> int:
        event_result_doc_find = EventResultDocFind(id=id, user_id=self.user_id)
        delete_result = await self.event_result_crud.delete_many(event_result_doc_find)
        return delete_result.deleted_count
