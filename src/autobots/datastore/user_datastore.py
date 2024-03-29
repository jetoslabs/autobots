from typing import List, Literal

from fastapi import HTTPException, UploadFile, BackgroundTasks
from loguru import logger
from pydantic import HttpUrl
from pymongo.database import Database
from pymongo.results import DeleteResult

from src.autobots.api.webhook import Webhook
from src.autobots.conn.aws.s3 import S3, get_s3
from src.autobots.conn.pinecone.pinecone import Pinecone, get_pinecone
from src.autobots.conn.unstructured_io.unstructured_io import get_unstructured_io, PartitionParametersParams
from src.autobots.datastore.datastore_meta_crud import DatastoreMetaCRUD
from src.autobots.datastore.datastore import Datastore
from src.autobots.datastore.datastore_meta_doc_model import DatastoreMetaDocCreate, DatastoreMetaDoc, DatastoreMetaDocFind
from src.autobots.datastore.datastore_result.datastore_result_doc_model import DatastoreResultCreate, DatastoreResultDoc, \
    DatastoreResultUpdate
from src.autobots.datastore.datastore_result.user_datastore_result import UserDatastoreResult
from src.autobots.event_result.event_result_model import EventResultStatus
from src.autobots.user.user_orm_model import UserORM


class UserDatastore():

    def __init__(self, user: UserORM, db: Database, s3: S3 = get_s3(), pinecone: Pinecone = get_pinecone()):
        self.datastore = Datastore(s3, pinecone, get_unstructured_io())
        self.user = user
        self.db = db
        self.datastore_meta_crud = DatastoreMetaCRUD(self.db)
        self.user_datastore_result = UserDatastoreResult(user, db)

    async def init(self, name: str) -> DatastoreMetaDoc:
        self.datastore.init(name)
        datastore_meta_doc_create = DatastoreMetaDocCreate(user_id=str(self.user.id), datastore_id=self.datastore.id,
                                                           name=self.datastore.name)
        user_datastore_meta = await self.datastore_meta_crud.insert_one(datastore_meta_doc_create)
        return user_datastore_meta

    async def hydrate(self, datastore_id: str) -> Datastore:
        datastore_meta_doc_find = DatastoreMetaDocFind(user_id=str(self.user.id), datastore_id=datastore_id)
        datastore_metas = await self.datastore_meta_crud.find(datastore_meta_doc_find)
        if len(datastore_metas) != 1:
            raise HTTPException(404, "Datastore not found")
        datastore_meta = datastore_metas[0]
        datastore = self.datastore.hydrate(datastore_meta.datastore_id)
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

    async def put_resource_async(
            self,
            datastore_id: str,
            data: str | None = None,
            files: List[UploadFile] | None = None,
            urls: List[HttpUrl] | None = None,
            chunk_size: int = 500,
            ocr_detail: Literal["low", "medium", "high"] = "low",
            background_tasks: BackgroundTasks | None = None,
            webhook: Webhook | None = None,
    ) -> DatastoreResultDoc | None:
        user_datastore = await self.hydrate(datastore_id)
        if user_datastore is None:
            raise HTTPException(404, "Datastore not found")
        datastore_result_create = DatastoreResultCreate(status=EventResultStatus.processing.value)
        datastore_result_doc = await self.user_datastore_result.create_datastore_result(datastore_result_create)

        if background_tasks:
            # Run in background
            background_tasks.add_task(
                self.put_resource,
                datastore_result_doc=datastore_result_doc,
                user_datastore_result=self.user_datastore_result,
                user_datastore=user_datastore,
                data=data,
                files=files,
                urls=urls,
                chunk_size=chunk_size,
                ocr_detail=ocr_detail,
                webhook=webhook
            )
        else:
            # For testing
            await self.put_resource(
                datastore_result_doc=datastore_result_doc,
                user_datastore_result=self.user_datastore_result,
                user_datastore=user_datastore,
                data=data,
                files=files,
                urls=urls,
                chunk_size=chunk_size,
                ocr_detail=ocr_detail,
                webhook=webhook
            )

        return datastore_result_doc

    async def put_resource(
            self,
            datastore_result_doc: DatastoreResultDoc,
            user_datastore_result: UserDatastoreResult,
            user_datastore: Datastore,
            data: str | None = None,
            files: List[UploadFile] | None = None,
            urls: List[HttpUrl] | None = None,
            chunk_size: int = 500,
            ocr_detail: Literal["low", "medium", "high"] = "low",
            webhook: Webhook | None = None
    ) -> DatastoreResultDoc:
        if data:
            try:
                datastore_results_1 = await user_datastore.put_data(data, chunk_token_size=chunk_size)
                datastore_result_doc.result.status_for = datastore_result_doc.result.status_for + datastore_results_1
                datastore_result_doc = await user_datastore_result.update_datastore_result(
                    datastore_result_doc.id, DatastoreResultUpdate(**datastore_result_doc.model_dump())
                )
            except Exception as e:
                logger.error(str(e))

        # Setup PartitionParametersParams for Unstructured_IO to be used in put_files or put_urls
        hi_res_model_name = "yolox"
        if ocr_detail == "low": hi_res_model_name = "yolox_quantized" # noqa E701
        elif ocr_detail == "medium": hi_res_model_name = "yolox" # noqa E701
        elif ocr_detail == "high": hi_res_model_name = "chipper" # noqa E701

        partition_parameters_params = PartitionParametersParams(
            combine_under_n_chars=chunk_size,
            strategy="hi_res",
            hi_res_model_name=hi_res_model_name,
            pdf_infer_table_structure=True
        )

        if files:
            try:
                datastore_results_2 = await user_datastore.put_files(files, partition_parameters_params)
                datastore_result_doc.result.status_for = datastore_result_doc.result.status_for + datastore_results_2
                datastore_result_doc = await user_datastore_result.update_datastore_result(
                    datastore_result_doc.id, DatastoreResultUpdate(**datastore_result_doc.model_dump())
                )
            except Exception as e:
                logger.error(str(e))
        if urls:
            try:
                datastore_results_3 = await user_datastore.put_urls(urls, partition_parameters_params)
                datastore_result_doc.result.status_for = datastore_result_doc.result.status_for + datastore_results_3
                datastore_result_doc = await user_datastore_result.update_datastore_result(
                    datastore_result_doc.id, DatastoreResultUpdate(**datastore_result_doc.model_dump())
                )
            except Exception as e:
                logger.error(str(e))

        datastore_result_doc.status = EventResultStatus.success
        datastore_result_doc = await user_datastore_result.update_datastore_result(
            datastore_result_doc.id, DatastoreResultUpdate(**datastore_result_doc.model_dump())
        )

        if webhook:
            await webhook.send(datastore_result_doc.model_dump())
        return datastore_result_doc

    async def get_datastore_put_result(self, datastore_put_result_id: str) -> DatastoreResultDoc | None:
        return await self.user_datastore_result.get_datastore_result(datastore_put_result_id)
