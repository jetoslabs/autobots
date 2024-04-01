import uuid
from io import BytesIO
from typing import Annotated, List, Literal
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from loguru import logger
from pydantic import HttpUrl
from pymongo.database import Database

from src.autobots import SettingsProvider
from src.autobots.action.action.common_action_models import TextObj
from src.autobots.api.webhook import Webhook
from src.autobots.auth.security import get_user_from_access_token
from src.autobots.conn.unstructured_io.unstructured_io import PartitionParametersParams
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.datastore.datastore_meta_doc_model import DatastoreMetaDoc
from src.autobots.datastore.datastore_result.datastore_result_doc_model import DatastoreResultDoc
from src.autobots.datastore.user_datastore import UserDatastore
from src.autobots.user.user_orm_model import UserORM
from src.autobots.conn.aws.aws_s3 import get_s3_for_image_upload

router = APIRouter(prefix=SettingsProvider.sget().API_DATASTORE, tags=[SettingsProvider.sget().API_DATASTORE])


@router.post("/")
async def create_datastore(
        name: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> DatastoreMetaDoc:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        user_datastore_meta = await UserDatastore(user_orm, db).init(name)
        return user_datastore_meta
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500, "unable to create datastore")


@router.get("/")
async def list_datastore(
        limit: int = 100, offset: int = 0,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> List[DatastoreMetaDoc]:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        user_datastore_meta = await UserDatastore(user_orm, db).list(limit, offset)
        return user_datastore_meta
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500, "unable to list datastore")


@router.get("/{name}")
async def get_datastore(
        name: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> DatastoreMetaDoc:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        user_datastore_meta = await UserDatastore(user_orm, db).get(name)
        return user_datastore_meta
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500, "unable to get datastore")


@router.post("/{id}/store_text")
async def store_text(
        datastore_id: str,
        text: TextObj,
        chunk_token_size: int = 512,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
):
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        user_datastore = await UserDatastore(user_orm, db).hydrate(datastore_id)
        await user_datastore.put_data(data=text.text, chunk_token_size=chunk_token_size)
        return {"done": "ok"}
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500, "Error while storing text in datastore")


@router.post("/{id}/store_file")
async def upload_files(
        datastore_id: str,
        files: Annotated[list[UploadFile], File(description="Multiple files as UploadFile")],
        chunk_size: int = 500,
        ocr_detail: Literal["low", "medium", "high"] = "low",
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
):
    try:
        user = UserORM(id=UUID(user_res.user.id))
        user_datastore = await UserDatastore(user, db).hydrate(datastore_id)

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
        await user_datastore.put_files(files, partition_parameters_params)
        return {"done": "ok"}
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500, "Error while storing files in datastore")

@router.post("/{id}/store_image_to_s3")
async def upload_image_files_to_s3(
        files: Annotated[List[UploadFile], File(description="file as UploadFile")],
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token)
) -> List[HttpUrl]:
    try:
        user = UserORM(id=UUID(user_res.user.id))
        random_uuid = uuid.uuid4()
        s3 = get_s3_for_image_upload(object_prefix=f'images/claid/{user.id}/{random_uuid}')

        result = []
        for file in files:
            # Convert BinaryIO to BytesIO
            bytes_io = BytesIO(await file.read())
            object_url = s3.put_file_obj(file_obj=bytes_io, filename=file.filename)
            result.append(object_url)
        return result

    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500, "Error while storing files in datastore")

@router.post("/{id}/store_urls")
async def store_urls(
        datastore_id: str,
        urls: List[HttpUrl],
        chunk_size: int = 500,
        ocr_detail: Literal["low", "medium", "high"] = "low",
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
):
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        user_datastore = await UserDatastore(user_orm, db).hydrate(datastore_id)

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

        await user_datastore.put_urls(urls=urls, partition_parameters_params=partition_parameters_params)
        return {"done": "ok"}
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500, "Error while storing URLs in datastore")


@router.post("/{id}/search")
async def search(
        datastore_id: str,
        query: TextObj,
        top_k: int = 10,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> List[str]:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        user_datastore = await UserDatastore(user_orm, db).hydrate(datastore_id)
        results = await user_datastore.search(query=query.text, top_k=top_k)
        return results
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500, "Error while search in datastore")


@router.delete("/{id}")
async def delete_datastore(
        datastore_id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> DatastoreMetaDoc:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        datastore_meta_doc = await UserDatastore(user_orm, db).get_by_datastore_id(datastore_id)
        if datastore_meta_doc is None:
            raise HTTPException(400, "Datastore_meta_doc not found")
        delete_result = await UserDatastore(user_orm, db).delete(datastore_id)
        deleted_count = delete_result.deleted_count
        if deleted_count != 1:
            raise HTTPException(500, "Error in deleting datastore_meta_doc")
        return datastore_meta_doc
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500, "Error while deleting datastore")


@router.post("/{id}/store_data/async")
async def store_data_async(
        background_tasks: BackgroundTasks,
        datastore_id: str,
        text: TextObj,
        webhook: Webhook | None = None,
        chunk_size: int = 500,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> DatastoreResultDoc | None:
    try:
        user = UserORM(id=UUID(user_res.user.id))
        user_datastore = UserDatastore(user, db)
        datastore_result_doc = await user_datastore.put_resource_async(
            datastore_id=datastore_id,
            data=text.text,
            files=None,
            urls=None,
            chunk_size=chunk_size,
            background_tasks=background_tasks,
            webhook=webhook
        )
        return datastore_result_doc
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500, "Error while storing data in datastore")


@router.post("/{id}/store_files/async")
async def store_files_async(
        background_tasks: BackgroundTasks,
        datastore_id: str,
        files: Annotated[list[UploadFile], File(description="Multiple files as UploadFile")],
        webhook: Webhook | None = None,
        chunk_size: int = 500,
        ocr_detail: Literal["low", "medium", "high"] = "low",
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> DatastoreResultDoc | None:
    try:
        user = UserORM(id=UUID(user_res.user.id))
        user_datastore = UserDatastore(user, db)
        datastore_result_doc = await user_datastore.put_resource_async(
            datastore_id=datastore_id,
            data=None,
            files=files,
            urls=None,
            chunk_size=chunk_size,
            ocr_detail=ocr_detail,
            background_tasks=background_tasks,
            webhook=webhook
        )
        return datastore_result_doc
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500, "Error while storing files in datastore")


@router.post("/{id}/store_urls/async")
async def store_urls_async(
        background_tasks: BackgroundTasks,
        datastore_id: str,
        urls: List[HttpUrl],
        webhook: Webhook | None = None,
        chunk_size: int = 500,
        ocr_detail: Literal["low", "medium", "high"] = "low",
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> DatastoreResultDoc | None:
    try:
        user = UserORM(id=UUID(user_res.user.id))
        user_datastore = UserDatastore(user, db)
        datastore_result_doc = await user_datastore.put_resource_async(
            datastore_id=datastore_id,
            data=None,
            files=None,
            urls=urls,
            chunk_size=chunk_size,
            ocr_detail=ocr_detail,
            background_tasks=background_tasks,
            webhook=webhook
        )
        return datastore_result_doc
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500, "Error while storing urls in datastore")


@router.get("/result/{datastore_put_result_id}")
async def get_datastore_put_result(
        datastore_put_result_id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
):
    try:
        user = UserORM(id=UUID(user_res.user.id))
        user_datastore = UserDatastore(user, db)
        return await user_datastore.get_datastore_put_result(datastore_put_result_id)
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500, "Internal server error")
