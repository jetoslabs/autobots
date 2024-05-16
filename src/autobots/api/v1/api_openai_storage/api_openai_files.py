from typing import Annotated, List

import gotrue
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from openai import BadRequestError
from openai.types import FileObject, FileDeleted

from src.autobots import SettingsProvider
from src.autobots.auth.security import get_user_from_access_token
from src.autobots.conn.openai.openai_client import get_openai
from src.autobots.conn.openai.openai_files.openai_files_model import FileCreate, FileList, FileRetrieve, FileContent, \
    FileDelete

router = APIRouter(prefix=f"{SettingsProvider.sget().API_OPENAI_STORAGE}/files", tags=[SettingsProvider.sget().API_OPENAI_STORAGE])


@router.post("/")
async def upload_file(
        file: Annotated[UploadFile, File(description="File as UploadFile")],
        # background_tasks: BackgroundTasks,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        # db: Database = Depends(get_mongo_db)
) -> FileObject:
    # user = UserORM(id=UUID(user_res.user.id))
    openai_file_client = get_openai().openai_files
    # background_tasks.add_task(openai_file_client.create, file_create)
    file_create = FileCreate(
        file=(file.filename, await file.read(), file.content_type),
        purpose="assistants"
    )
    file_obj = await openai_file_client.create(file_create)
    return file_obj


@router.get("/list")
async def list_files_info(
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token)
) -> List[FileObject]:
    openai_file_client = get_openai().openai_files
    file_list = FileList(extra_query={"user_id": user_res.user.id})
    files_gen = await openai_file_client.list(file_list)
    return files_gen.data


@router.get("/")
async def get_file_info(
        file_id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token)
) -> FileObject:
    openai_file_client = get_openai().openai_files
    file_retrieve = FileRetrieve(
        file_id=file_id,
        extra_query={"user_id": user_res.user.id}
    )
    file = await openai_file_client.retrieve(file_retrieve)
    return file


@router.get("/content")
async def get_file(
        file_id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token)
) -> str:
    try:
        openai_file_client = get_openai().openai_files
        file_content = FileContent(
            file_id=file_id,
            extra_query={"user_id": user_res.user.id}
        )
        resp = await openai_file_client.retrieve_content(file_content)
        return resp.text
    except BadRequestError or Exception as e:
        if isinstance(e, BadRequestError):
            raise HTTPException(status_code=e.status_code, detail=e.message)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/")
async def delete_file(
        file_id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token)
) -> FileDeleted:
    openai_file_client = get_openai().openai_files
    file_delete = FileDelete(
        file_id=file_id,
        extra_query={"user_id": user_res.user.id}
    )
    file_deleted = await openai_file_client.delete(file_delete)
    return file_deleted
