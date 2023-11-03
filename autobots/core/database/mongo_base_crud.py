from typing import TypeVar, Generic, List

from bson import ObjectId
from fastapi import Depends, HTTPException
from pydantic import BaseModel
from pymongo.collection import Collection, ReturnDocument
from pymongo.database import Database
from pymongo.results import DeleteResult

from autobots.core.database.mongo_base import get_mongo_db

DocType = TypeVar("DocType", bound=BaseModel)
DocCreateType = TypeVar("DocCreateType", bound=BaseModel)
DocFindType = TypeVar("DocFindType", bound=BaseModel)
DocUpdateType = TypeVar("DocUpdateType", bound=BaseModel)


class CRUDBase(Generic[DocType, DocCreateType, DocFindType, DocUpdateType]):

    def __init__(self, db: Database = Depends(get_mongo_db)):
        self.document: Collection = db[DocType.__collection__]

    async def insert_one(self, create_doc: DocCreateType) -> DocType:
        insert_result = self.document.insert_one(create_doc.model_dump())
        inserted_result = await self.find_by_id(insert_result.inserted_id)
        return inserted_result

    async def find_by_id(self, id: str) -> DocType:
        object_id = ObjectId(id)
        doc = self.document.find_one({"_id": object_id})
        doc["_id"] = str(doc.get("_id"))
        return DocType.model_validate(doc)

    async def find(self, doc_find: DocFindType, limit: int = 100, offset: int = 0) -> List[DocType]:
        find_params = {}
        for key, value in doc_find.model_dump().items():
            if value:
                if key == "id":
                    find_params["_id"] = ObjectId(value)
                else:
                    find_params[key] = value
        if len(find_params) == 0:
            return []

        cursor = self.document.find(find_params)
        docs = []

        skipped = 0
        filled = 0
        for doc in cursor:
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
            doc_type = DocType.model_validate(doc)
            docs.append(doc_type)

        return docs

    async def delete_many(self, doc_find: DocFindType) -> DeleteResult:
        find_params = {}
        for key, value in doc_find.model_dump().items():
            if value:
                if key == "id":
                    find_params["_id"] = ObjectId(value)
                else:
                    find_params[key] = value

        delete_result = self.document.delete_many(find_params)
        return delete_result

    async def update_one(self, doc_update: DocUpdateType) -> DocType:
        if not doc_update.id or not doc_update.user_id:
            raise HTTPException(405, "Cannot find Doc to update")

        update_params = {}
        for key, value in doc_update.model_dump().items():
            if value:
                if key == "id":
                    update_params["_id"] = ObjectId(value)
                else:
                    update_params[key] = value

        updated_action_doc = self.document.find_one_and_update(
            filter={"_id": update_params.get("_id"), "user_id": update_params.get("user_id")},
            update={"$set": update_params},
            return_document=ReturnDocument.AFTER
        )
        if updated_action_doc is None:
            raise HTTPException(405, "Unable to update doc")

        updated_action_doc.__dict__["_id"] = str(updated_action_doc.get("_id"))
        doc_type = DocType.model_validate(updated_action_doc)
        return doc_type




