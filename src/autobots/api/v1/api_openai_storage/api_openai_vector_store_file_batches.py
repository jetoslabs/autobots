from typing import List, Literal

import gotrue
from fastapi import APIRouter, Depends
from openai.types.beta.vector_stores import VectorStoreFileBatch, VectorStoreFile, VectorStoreFileDeleted

from src.autobots import SettingsProvider
from src.autobots.auth.security import get_user_from_access_token
from src.autobots.conn.openai.openai_client import get_openai
from src.autobots.conn.openai.openai_vector_stores.openai_vector_store_file_batches.openai_vector_store_file_batches_model import \
    CreateVectorStoreFileBatch, ListVectorStoreFilesInBatch, RetrieveVectorStoreFileBatch
from src.autobots.conn.openai.openai_vector_stores.openai_vector_store_files.openai_vector_store_files_model import \
    DeleteVectorStoreFile

router = APIRouter(prefix=f"{SettingsProvider.sget().API_OPENAI_STORAGE}/vector_store_file_batches",
                   tags=[SettingsProvider.sget().API_OPENAI_STORAGE])


@router.post("/")
async def create_vector_store_files(
        vector_store_files: CreateVectorStoreFileBatch,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
) -> VectorStoreFileBatch:
    # user = UserORM(id=UUID(user_res.user.id))
    openai_vector_store_file_batches = get_openai().openai_vector_store_file_batches
    files = await openai_vector_store_file_batches.create(vector_store_files)
    return files


@router.get("/list")
async def list_vector_store_files(
        vector_store_id: str,
        batch_id: str,
        limit: int | None = 10,
        order: Literal['desc', 'asc'] | None = 'desc',
        after: str | None = None,
        before: str | None = None,
        filter: Literal['in_progress', 'completed', 'failed', 'cancelled'] | None = None,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
) -> List[VectorStoreFile]:
    openai_vector_store_file_batches = get_openai().openai_vector_store_file_batches
    vector_store_files_in_batch = ListVectorStoreFilesInBatch(
        vector_store_id=vector_store_id,
        batch_id=batch_id,
        limit=limit,
        order=order,
        after=after,
        before=before,
        filter=filter,
    )
    vector_store_files = await openai_vector_store_file_batches.list(vector_store_files_in_batch)
    return vector_store_files


@router.get("/")
async def get_vector_store_files(
        retrieve_vector_store_files: RetrieveVectorStoreFileBatch,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token)
) -> VectorStoreFileBatch:
    openai_vector_store_file_batches = get_openai().openai_vector_store_file_batches
    file_batch = await openai_vector_store_file_batches.retrieve(retrieve_vector_store_files)
    return file_batch


@router.delete("/")
async def delete_vector_store_files(
        vector_store: DeleteVectorStoreFile,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token)
) -> VectorStoreFileDeleted:
    openai_vector_store_files = get_openai().openai_vector_store_files
    deleted = await openai_vector_store_files.delete(vector_store)
    return deleted
