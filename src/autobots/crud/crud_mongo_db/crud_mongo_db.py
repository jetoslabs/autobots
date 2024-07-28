from functools import lru_cache
from typing import Any, List, Dict

from bson import ObjectId
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase, AsyncIOMotorClient
from pymongo import ReturnDocument, DESCENDING
from pymongo.results import DeleteResult

from src.autobots.data_model.context import Context
from src.autobots.core.settings import Settings, SettingsProvider
from src.autobots.crud.crud_protocol import CRUDProtocol, DataCreateType, DataFindType, DataUpdateType, \
    DataType, LiteDataType, CreateData, ReadByIdData, FindManyData, FindPageData, UpdateData, FindOneData
from src.autobots.exception.app_exception import AppException
from src.autobots.crud.crud_mongo_db.mongo_db_conn_protocol import MongoDBConnProtocol


class MongoDBCRUD(
    MongoDBConnProtocol,
    CRUDProtocol[DataType, LiteDataType, DataCreateType, DataFindType, DataUpdateType]
):
    """
    Create MongoDBCRUD.client or _client only once, reuse the database many times.
    How will you handle case when conn is broken/closed in middle of use?
    """

    @staticmethod
    @lru_cache()
    async def client(ctx: Context) -> AsyncIOMotorClient:
        settings = SettingsProvider.sget()
        return await MongoDBCRUD._client(ctx, settings)

    @staticmethod
    async def _client(ctx: Context, settings: Settings) -> AsyncIOMotorClient:
        # moved ?retryWrites=true&w=majority out of secrets as github unable to handle it
        # TODO: move it back to secrets
        mongo_conn = f"{settings.MONGO_CONN}?retryWrites=true&w=majority"
        return AsyncIOMotorClient(mongo_conn)

    @staticmethod
    async def close_client(ctx: Context, client: AsyncIOMotorClient) -> None:
        return client.close()

    @staticmethod
    async def database(ctx: Context, settings: Settings, client: AsyncIOMotorClient) -> AsyncIOMotorDatabase:
        return client.get_database(settings.MONGO_DATABASE)

    @staticmethod
    async def collection(ctx: Context, settings: Settings, database: AsyncIOMotorDatabase,
                         collection_name: str) -> AsyncIOMotorCollection:
        return database.get_collection(collection_name)

    @staticmethod
    async def create(create_data: List[CreateData]) -> List[DataType | Exception]:
        create_output: List[DataType | Exception] = []
        for create_one in create_data:
            try:
                insert_result = await create_one.data_source.insert_one(create_one.create_params.model_dump())
                read_data = ReadByIdData(
                    ctx=create_one.ctx,
                    data_source=create_one.data_source,
                    data_type=create_one.data_type,
                    lite_data_type=create_one.lite_data_type,
                    read_id=str(insert_result.inserted_id),
                )
                result = await MongoDBCRUD._read_by_id(read_data)
                create_output.append(result)
            except Exception as e:
                logger.bind(**create_one.ctx.model_dump()).exception(str(e))
                e = AppException(detail=str(e), http_status=422)
                create_output.append(e)
        return create_output

    @staticmethod
    async def _read_by_id(read_data: ReadByIdData) -> DataType | Exception:
        try:
            object_id = ObjectId(read_data.read_id)
            doc: dict = await read_data.data_source.find_one({"_id": object_id})
            assert doc is not None
            doc["_id"] = str(doc.get("_id"))
            return read_data.data_type.model_validate(doc)
        except Exception as e:
            logger.bind(**read_data.ctx.model_dump()).error(str(e))
            return AppException(detail=str(e), http_status=404)

    @staticmethod
    async def find_one(find_data: FindOneData) -> DataType | Exception:
        find_params = await MongoDBCRUD._build_filter(find_data.ctx, find_data.find_params, find_data.or_find_queries)
        match find_params:
            case Exception():
                return find_params
            case dict():
                doc = await find_data.data_source.find_one(find_params)
                match doc:
                    case None:
                        return AppException(detail=f"Cannot find data in collection {find_data.data_source.name}",
                                            http_status=404)
                    case _:
                        doc["_id"] = str(doc.get("_id"))
                        return find_data.data_type.model_validate(doc)

    @staticmethod
    async def find_paginated(find_paginated_data: FindManyData) -> FindPageData | Exception:
        docs = await MongoDBCRUD.find_many(find_paginated_data)
        match docs:
            case Exception():
                return docs

        total_count = await MongoDBCRUD.count(find_paginated_data)
        match total_count:
            case Exception():
                return total_count
        return FindPageData(docs=docs, total_count=total_count, limit=find_paginated_data.limit,
                            offset=find_paginated_data.offset)

    @staticmethod
    async def find_many(find_data: FindManyData) -> List[LiteDataType] | Exception:
        find_params = await MongoDBCRUD._build_filter(find_data.ctx, find_data.find_params, find_data.or_find_queries)
        if isinstance(find_params, Exception) or len(find_params) == 0:
            return find_params

        model_fields = find_data.lite_data_type.model_fields.keys()
        fields_to_select = {}
        for field in model_fields:
            match field:
                case str():
                    fields_to_select[field] = 1
                case dict():
                    #  TODO: handle case
                    pass

        cursor = find_data.data_source.find(find_params, fields_to_select)
        cursor.allow_disk_use(True)
        cursor.sort([("updated_at", DESCENDING), ("created_at", DESCENDING)]).skip(
            find_data.offset * find_data.limit).limit(find_data.limit)
        docs = []

        async for doc in cursor:
            try:
                # Mongo Result field _id has ObjectId, converting it to str for pydantic model
                doc["_id"] = str(doc.get("_id"))
                doc_type = find_data.lite_data_type.model_validate(doc)
                docs.append(doc_type)
            except Exception as e:
                logger.bind(**find_data.ctx.to_dict(), doc=doc).error(str(e))

        return docs

    @staticmethod
    async def update(update_data: List[UpdateData]) -> List[DataType | Exception]:
        update_output: List[DataType | Exception] = []
        for update_one in update_data:
            if not update_one.update_params.id or not update_one.update_params.user_id:
                raise AppException("Cannot find Doc to update", 405)

            update_params = {}
            for key, value in update_one.update_params.model_dump().items():
                if value is not None:
                    if key == "id":
                        update_params["_id"] = ObjectId(value)
                    else:
                        update_params[key] = value

            updated_action_doc: dict | None = await update_one.data_source.find_one_and_update(
                filter={"_id": update_params.get("_id"), "user_id": update_params.get("user_id")},
                update={"$set": update_params},
                return_document=ReturnDocument.AFTER
            )
            if updated_action_doc is None:
                e = AppException("Cannot find Doc to update", 405)
                update_output.append(e)
            else:
                updated_action_doc["_id"] = str(updated_action_doc.get("_id"))
                doc = update_one.data_type.model_validate(updated_action_doc)
                update_output.append(doc)
        return update_output

    @staticmethod
    async def delete_many(find_data: FindManyData) -> DeleteResult | Exception:
        find_params = await MongoDBCRUD._build_filter(find_data.ctx, find_data.find_params, find_data.or_find_queries)
        if isinstance(find_params, Exception):
            return find_params

        delete_result = await find_data.data_source.delete_many(find_params)
        return delete_result

    @staticmethod
    async def count(find_data: FindManyData) -> int | Exception:
        find_params = await MongoDBCRUD._build_filter(find_data.ctx, find_data.find_params, find_data.or_find_queries)
        count = await find_data.data_source.count_documents(find_params)
        return count

    @staticmethod
    async def _build_filter(
            ctx: Context, doc_find: DataFindType, or_find_queries: List[DataFindType] | None = None
    ) -> Dict[str, Any] | Exception:
        query_filter = {}
        filter1 = await MongoDBCRUD._build_find_params(ctx, doc_find)
        if doc_find and (not or_find_queries or len(or_find_queries) == 0):
            query_filter = filter1
        elif or_find_queries and len(or_find_queries) > 0:
            query_filter["$or"] = [filter1]
            for query in or_find_queries:
                filter2 = await MongoDBCRUD._build_find_params(ctx, query)
                query_filter["$or"] += [filter2]
        return query_filter

    @staticmethod
    async def _build_find_params(
            ctx: Context, doc_find: DataFindType
    ) -> Dict[str, Any] | Exception:
        try:
            find_params = {}
            for key, value in doc_find.model_dump().items():
                if value is not None:
                    if key == "id":
                        find_params["_id"] = ObjectId(value)
                    else:
                        find_params[key] = value
            return find_params
        except Exception as e:
            logger.bind(**ctx.model_dump()).exception(str(e))
            e = AppException(detail=str(e), http_status=500)
            return e
