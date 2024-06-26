from typing import List

from bson import ObjectId
from fastapi import HTTPException
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import DESCENDING
from pymongo.collection import ReturnDocument
from pymongo.results import DeleteResult

from src.autobots.datastore.datastore_meta_doc_model import DatastoreMetaDoc, DatastoreMetaDocCreate, DatastoreMetaDocFind, \
    DatastoreMetaDocUpdate


class DatastoreMetaCRUD:

    def __init__(self, db: AsyncIOMotorDatabase):
        self.document: AsyncIOMotorCollection = db[DatastoreMetaDoc.__collection__]

    async def insert_one(self, datastore_meta_doc_create: DatastoreMetaDocCreate) -> DatastoreMetaDoc:
        datastore_meta_doc_find = DatastoreMetaDocFind(
            name=datastore_meta_doc_create.name, user_id=datastore_meta_doc_create.user_id
        )
        datastore_meta_doc_found = await self.find(datastore_meta_doc_find)
        if len(datastore_meta_doc_found) > 0:
            raise HTTPException(400, "Datastore_Meta not unique")
        insert_result = await self.document.insert_one(datastore_meta_doc_create.model_dump())
        inserted_datastore_meta = await self._find_by_object_id(insert_result.inserted_id)
        return inserted_datastore_meta

    async def _find_by_object_id(self, id: str) -> DatastoreMetaDoc:
        object_id = ObjectId(id)
        doc = await self.document.find_one({"_id": object_id})
        doc["_id"] = str(doc.get("_id"))
        return DatastoreMetaDoc.model_validate(doc)

    async def find(
            self, datastore_meta_doc_find: DatastoreMetaDocFind, limit: int = 100, offset: int = 0
    ) -> List[DatastoreMetaDoc]:
        find_params = {}
        for key, value in datastore_meta_doc_find.model_dump().items():
            if value is not None:
                if key == "id":
                    find_params["_id"] = ObjectId(value)
                else:
                    find_params[key] = value
        if len(find_params) == 0:
            return []

        cursor = self.document.find(find_params)
        cursor.sort([("updated_at", DESCENDING), ("created_at", DESCENDING)]).skip(offset).limit(limit)
        datastore_meta_docs = []

        skipped = 0
        filled = 0
        async for doc in cursor:
            action_doc = None
            try:
                # skipping records
                if skipped < offset * limit:
                    skipped = skipped + 1
                    continue
                # break if limit reached
                if filled >= limit:
                    break
                filled = filled + 1
                # Mongo Result field _id has ObjectId, converting it to str for pydantic model
                doc["_id"] = str(doc.get("_id"))
                datastore_meta_doc = DatastoreMetaDoc.model_validate(doc)
                datastore_meta_docs.append(datastore_meta_doc)
            except Exception as e:
                logger.bind(action_doc=action_doc).error(f"Error while parsing action doc: {e}, skipping to next")

        return datastore_meta_docs

    async def delete_many(self, datastore_meta_doc_find: DatastoreMetaDocFind) -> DeleteResult:
        find_params = {}
        for key, value in datastore_meta_doc_find.model_dump().items():
            if value is not None:
                if key == "id":
                    find_params["_id"] = ObjectId(value)
                else:
                    find_params[key] = value

        delete_result = await self.document.delete_many(find_params)
        return delete_result

    async def delete_one(self, id: str) -> DeleteResult:
        datastore_meta_doc = await self._find_by_object_id(id)
        if datastore_meta_doc is None:
            raise HTTPException(405, "Unable to find datastore_meta_doc to delete")
        delete_result = await self.document.delete_one({"_id": ObjectId(datastore_meta_doc.id)})
        return delete_result

    async def update_one(self, datastore_meta_doc_update: DatastoreMetaDocUpdate) -> DatastoreMetaDoc:
        update_params = {}
        for key, value in datastore_meta_doc_update.model_dump().items():
            if value is not None:
                if key == "id":
                    update_params["_id"] = ObjectId(value)
                else:
                    update_params[key] = value
        if not update_params["_id"] and not update_params["user_id"]:
            raise HTTPException(405, "Cannot find datastore_meta_doc to update")

        updated_datastore_meta_doc = await self.document.find_one_and_update(
            filter={"_id": update_params.get("_id"), "user_id": datastore_meta_doc_update.user_id},
            update={"$set": update_params},
            return_document=ReturnDocument.AFTER
        )
        if updated_datastore_meta_doc is None:
            raise HTTPException(405, "Unable to update datastore_meta_doc")

        updated_datastore_meta_doc["_id"] = str(updated_datastore_meta_doc.get("_id"))
        datastore_meta_doc = DatastoreMetaDoc.model_validate(updated_datastore_meta_doc)
        return datastore_meta_doc
