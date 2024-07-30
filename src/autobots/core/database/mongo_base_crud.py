from typing import TypeVar, Generic, List, Type, Dict, Any

from bson import ObjectId
from fastapi import HTTPException
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel
from pymongo import ReturnDocument, DESCENDING
from pymongo.results import DeleteResult

from src.autobots.core.logging.log_binder import LogBinder

DocType = TypeVar("DocType", bound=BaseModel)
LiteDocType = TypeVar("LiteDocType", bound=BaseModel)  # Minimal version of DocType, used in listing. Takes less memory.
DocCreateType = TypeVar("DocCreateType", bound=BaseModel)
DocFindType = TypeVar("DocFindType", bound=BaseModel)
DocUpdateType = TypeVar("DocUpdateType", bound=BaseModel)


class DocFindPage(BaseModel):
    docs: List[LiteDocType]
    total_count: int
    limit: int
    offset: int


class CRUDBase(Generic[DocType, LiteDocType, DocCreateType, DocFindType, DocUpdateType]):

    def __init__(self, doc_model: Type[DocType], lite_doc_model: Type[LiteDocType], collection: AsyncIOMotorCollection):
        self.doc_model = doc_model
        self.lite_doc_model = lite_doc_model
        self.document: AsyncIOMotorCollection = collection  # db[DocType.__collection__]

    async def insert_one(self, create_doc: DocCreateType) -> DocType | Exception:
        try:
            insert_result = await self.document.insert_one(create_doc.model_dump())
            inserted_result = await self._find_by_id(insert_result.inserted_id)
            return inserted_result
        except Exception as e:
            logger.bind(create_doc=create_doc).error(str(e))
            return e

    async def _find_by_id(self, id: str) -> DocType:
        object_id = ObjectId(id)
        doc = await self.document.find_one({"_id": object_id})
        doc["_id"] = str(doc.get("_id"))
        return self.doc_model.model_validate(doc)

    async def find_one(self, doc_find: DocFindType, or_find_queries: List[DocFindType] | None = None) -> DocType | None:
        find_params = await self._build_filter(doc_find, or_find_queries)
        if isinstance(find_params, Exception):
            return None
        doc = await self.document.find_one(find_params)
        if doc is None:
            return None
        doc["_id"] = str(doc.get("_id"))
        return self.doc_model.model_validate(doc)

    async def find_page(
            self,
            doc_find: DocFindType,
            or_find_queries: List[DocFindType] | None = None,
            limit: int = 100,
            offset: int = 0
    ) -> DocFindPage:
        find_params = await self._build_filter(doc_find, or_find_queries)
        if isinstance(find_params, Exception) or len(find_params) == 0:
            return DocFindPage(docs=[], total_count=0, limit=limit, offset=offset)

        docs = await self.find(doc_find=doc_find, or_find_queries=or_find_queries, limit=limit, offset=offset)

        # model_fields = self.lite_doc_model.model_fields.keys()
        # fields_to_select = {}
        # for field in model_fields:
        #     fields_to_select[field] = 1
        #
        # cursor = self.document.find(find_params, fields_to_select).allow_disk_use(True)
        # cursor.sort([("updated_at", DESCENDING), ("created_at", DESCENDING)]).skip(offset * limit).limit(limit)
        # docs = []
        #
        # async for doc in cursor:
        #     try:
        #         # Mongo Result field _id has ObjectId, converting it to str for pydantic model
        #         doc["_id"] = str(doc.get("_id"))
        #         doc_type = self.lite_doc_model.model_validate(doc)
        #         docs.append(doc_type)
        #     except Exception as e:
        #         logger.bind(**LogBinder().with_kwargs(doc_find=doc_find, doc=doc).get_bind_dict()).error(str(e))

        total_count = await self.count(find_params=find_params)

        return DocFindPage(docs=docs, total_count=total_count, limit=limit, offset=offset)

    async def find(
            self,
            doc_find: DocFindType,
            or_find_queries: List[DocFindType] | None = None,
            limit: int = 100,
            offset: int = 0
    ) -> List[DocType]:
        find_params = await self._build_filter(doc_find, or_find_queries)
        if isinstance(find_params, Exception) or len(find_params) == 0:
            return []

        model_fields = self.lite_doc_model.model_fields.keys()
        fields_to_select = {}
        for field in model_fields:
            if isinstance(field, dict):
                for k, v in field.items():
                    fields_to_select[f"{k}.{field}"] = 1
            else:
                fields_to_select[field] = 1

        cursor = self.document.find(find_params, fields_to_select)
        cursor.allow_disk_use(True)
        cursor.sort([("updated_at", DESCENDING), ("created_at", DESCENDING)]).skip(offset * limit).limit(limit)
        docs = []

        async for doc in cursor:
            try:
                # Mongo Result field _id has ObjectId, converting it to str for pydantic model
                doc["_id"] = str(doc.get("_id"))
                doc_type = self.lite_doc_model.model_validate(doc)
                docs.append(doc_type)
            except Exception as e:
                logger.bind(**LogBinder().with_kwargs(doc_find=doc_find, doc=doc).get_bind_dict()).error(str(e))

        return docs

    async def count(self, find_params: Dict[str, Any]) -> int:
        count = await self.document.count_documents(find_params)
        return count

    async def delete_many(self, doc_find: DocFindType) -> DeleteResult | Exception:
        find_params = await self._build_filter(doc_find)
        if isinstance(find_params, Exception):
            return find_params

        delete_result = await self.document.delete_many(find_params)
        return delete_result

    async def update_one(self, doc_update: DocUpdateType) -> DocType | Exception:
        try:
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
        except Exception as e:
            logger.bind(doc_update=doc_update).exception(str(e))
            return e

    async def _build_filter(
            self, doc_find: DocFindType, or_find_queries: List[DocFindType] | None = None
    ) -> Dict[str, Any] | Exception:
        query_filter = {}
        filter1 = await self._build_find_params(doc_find.model_dump(exclude_none=True), {})
        if doc_find and (not or_find_queries or len(or_find_queries) == 0):
            query_filter = filter1
        elif or_find_queries and len(or_find_queries) > 0:
            query_filter["$or"] = [filter1]
            for query in or_find_queries:
                filter2 = await self._build_find_params(query.model_dump(exclude_none=True), {})
                query_filter["$or"] += [filter2]
        return query_filter

    async def _build_find_params(
            self, model_params: Dict[str, Any], mongo_params: Dict[str, Any], mongo_param_prefix: str = ""
    ) -> Dict[str, Any] | Exception:
        try:
            find_params = mongo_params
            for key, value in model_params.items():
                if value is not None:
                    if key == "id":
                        find_params[f"{mongo_param_prefix}_id"] = ObjectId(value)
                    else:
                        match value:
                            case dict():
                                new_find_params = await self._build_find_params(
                                    value,
                                    {},
                                    f"{mongo_param_prefix}{key}."
                                )
                                for param_key in new_find_params.keys():
                                    new_key = f"{mongo_param_prefix}{param_key}"
                                    find_params[new_key] = new_find_params[param_key]
                            case _:
                                find_params[f"{mongo_param_prefix}{key}"] = value
            return find_params
        except Exception as e:
            logger.exception(str(e))
            return e
