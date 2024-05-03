from typing import Annotated, List, Optional
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, UploadFile, File
from loguru import logger

from src.autobots import SettingsProvider
from src.autobots.auth.security import get_user_from_access_token
from src.autobots.conn.aws.aws_s3 import get_s3
from src.autobots.files.user_files import UserFiles
from src.autobots.files.user_files_model import FilesAndProcessingParams
from src.autobots.user.user_orm_model import UserORM

router = APIRouter(prefix=SettingsProvider.sget().API_FILES, tags=[SettingsProvider.sget().API_FILES])


@router.post("/")
async def upload_files(
        files: Annotated[List[UploadFile], File(description="Multiple files as UploadFile")],
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
) -> List[str]:
    try:
        user = UserORM(id=UUID(user_res.user.id))
        s3 = get_s3()
        settings = SettingsProvider.sget()
        user_files = UserFiles(user, s3, settings)

        uploaded = await user_files.upload_files(files)
        return uploaded
    except Exception as e:
        logger.error(str(e))
        raise


@router.get("/")
async def get_files(
        prefix: Optional[str] = None,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
) -> List[str]:
    try:
        user = UserORM(id=UUID(user_res.user.id))
        s3 = get_s3()
        user_files = UserFiles(user, s3)

        files = await user_files.list_files(prefix)
        return files
    except Exception as e:
        logger.error(str(e))
        raise


@router.delete("/")
async def delete_files(
        filenames: List[str],
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
) -> List[str]:
    try:
        user = UserORM(id=UUID(user_res.user.id))
        s3 = get_s3()
        settings = SettingsProvider.sget()
        user_files = UserFiles(user, s3, settings)

        deleted = await user_files.delete_files(filenames)
        await user_files.delete_downloaded_files(filenames)
        return deleted
    except Exception as e:
        logger.error(str(e))
        raise


@router.post("/process")
async def process_files(
        files_and_processing_params: FilesAndProcessingParams,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
) -> List[str]:
    try:
        user = UserORM(id=UUID(user_res.user.id))
        s3 = get_s3()
        settings = SettingsProvider.sget()
        user_files = UserFiles(user, s3, settings)

        processed_files = []
        async for processed_file in user_files.processed_file_and_yield(files_and_processing_params):
            processed_files.append(processed_file)
        return processed_files
    except Exception as e:
        logger.error(str(e))
        raise
