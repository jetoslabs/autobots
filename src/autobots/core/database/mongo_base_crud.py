from typing import TypeVar, Generic, List, Type, Dict, Any

from bson import ObjectId
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel
from pymongo import ReturnDocument, DESCENDING
from pymongo.results import DeleteResult

DocType = TypeVar("DocType", bound=BaseModel)
DocCreateType = TypeVar("DocCreateType", bound=BaseModel)
DocFindType = TypeVar("DocFindType", bound=BaseModel)
DocUpdateType = TypeVar("DocUpdateType", bound=BaseModel)


class DocFindPage(BaseModel):
    docs: List[DocType]
    total_count: int
    limit: int
    offset: int


class CRUDBase(Generic[DocType, DocCreateType, DocFindType, DocUpdateType]):

    def __init__(self, doc_model: Type[DocType], collection: AsyncIOMotorCollection):
        self.doc_model = doc_model
        self.document: AsyncIOMotorCollection = collection  # db[DocType.__collection__]

    async def insert_one(self, create_doc: DocCreateType) -> DocType:
        insert_result = await self.document.insert_one(create_doc.model_dump())
        inserted_result = await self.find_by_id(insert_result.inserted_id)
        return inserted_result

    async def find_by_id(self, id: str) -> DocType:
        object_id = ObjectId(id)
        doc = await self.document.find_one({"_id": object_id})
        doc["_id"] = str(doc.get("_id"))
        return self.doc_model.model_validate(doc)

    async def find_page(self, doc_find: DocFindType, limit: int = 100, offset: int = 0) -> DocFindPage:
        find_params = await self._build_find_params(doc_find)
        if len(find_params) == 0:
            return DocFindPage(docs=[], total_count=0, limit=limit, offset=offset)

        cursor = self.document.find(find_params)
        cursor.sort([("updated_at", DESCENDING), ("created_at", DESCENDING)]).skip(offset * limit).limit(limit)
        docs = []

        async for doc in cursor:
            # Mongo Result field _id has ObjectId, converting it to str for pydantic model
            doc["_id"] = str(doc.get("_id"))
            doc_type = self.doc_model.model_validate(doc)
            docs.append(doc_type)

        total_count = await self.count(find_params=find_params)

        return DocFindPage(docs=docs, total_count=total_count, limit=limit, offset=offset)

    async def find(self, doc_find: DocFindType, limit: int = 100, offset: int = 0) -> List[DocType]:
        find_params = await self._build_find_params(doc_find)
        if len(find_params) == 0:
            return []

        cursor = self.document.find(find_params)
        cursor.sort([("updated_at", DESCENDING), ("created_at", DESCENDING)]).skip(offset * limit).limit(limit)
        docs = []

        async for doc in cursor:
            # Mongo Result field _id has ObjectId, converting it to str for pydantic model
            doc["_id"] = str(doc.get("_id"))
            doc_type = self.doc_model.model_validate(doc)
            docs.append(doc_type)

        return docs

    async def count(self, find_params: Dict[str, Any]) -> int:
        count = await self.document.count_documents(find_params)
        return count

    async def delete_many(self, doc_find: DocFindType) -> DeleteResult:
        find_params = await self._build_find_params(doc_find)

        delete_result = await self.document.delete_many(find_params)
        return delete_result

    async def update_one(self, doc_update: DocUpdateType) -> DocType:
        if not doc_update.id or not doc_update.user_id:
            raise HTTPException(405, "Cannot find Doc to update")

        update_params = {}
        for key, value in doc_update.model_dump().items():
            if value is not None:
                if key == "id":
                    update_params["_id"] = ObjectId(value)
                else:
                    update_params[key] = value

        updated_action_doc = await self.document.find_one_and_update(
            filter={"_id": update_params.get("_id"), "user_id": update_params.get("user_id")},
            update={"$set": update_params},
            return_document=ReturnDocument.AFTER
        )
        if updated_action_doc is None:
            raise HTTPException(405, "Unable to update doc")

        updated_action_doc["_id"] = str(updated_action_doc.get("_id"))
        doc_type = self.doc_model.model_validate(updated_action_doc)
        return doc_type

    async def _build_find_params(self, doc_find: DocFindType) -> Dict[str, Any]:
        find_params = {}
        for key, value in doc_find.model_dump().items():
            if value is not None:
                if key == "id":
                    find_params["_id"] = ObjectId(value)
                else:
                    find_params[key] = value
        return find_params
