from typing import List, Literal

import gotrue
from fastapi import APIRouter, Depends
from openai.types.beta import VectorStore, VectorStoreDeleted

from src.autobots import SettingsProvider
from src.autobots.auth.security import get_user_from_access_token
from src.autobots.conn.openai.openai_client import get_openai
from src.autobots.conn.openai.openai_vector_stores.openai_vector_stores.openai_vector_stores_model import \
    CreateVectorStore, ListVectorStore, RetrieveVectorStore, UpdateVectorStore, DeleteVectorStore

router = APIRouter(prefix=f"{SettingsProvider.sget().API_OPENAI_STORAGE}/vector_stores", tags=[SettingsProvider.sget().API_OPENAI_STORAGE])


@router.post("/")
async def create_vector_store(
        new_vector_store: CreateVectorStore,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
) -> VectorStore:
    # user = UserORM(id=UUID(user_res.user.id))
    openai_vector_stores_client = get_openai().openai_vector_stores
    vector_store = await openai_vector_stores_client.create(new_vector_store)
    return vector_store


@router.get("/list")
async def list_vector_stores(
        limit: int = 10,
        order: Literal['desc', 'asc'] = 'desc',
        after: str | None = None,
        before: str | None = None,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
) -> List[VectorStore]:
    openai_vector_stores_client = get_openai().openai_vector_stores
    vector_stores = ListVectorStore(limit=limit, order=order, after=after, before=before)
    stores = await openai_vector_stores_client.list(vector_stores)
    return stores


@router.get("/")
async def get_vector_store(
        retrieve_vector_store: RetrieveVectorStore,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token)
) -> VectorStore:
    openai_vector_stores_client = get_openai().openai_vector_stores
    store = await openai_vector_stores_client.retrieve(retrieve_vector_store)
    return store


@router.put("/")
async def update_vector_store(
        vector_store: UpdateVectorStore,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token)
) -> VectorStore:
    openai_vector_stores_client = get_openai().openai_vector_stores
    store = await openai_vector_stores_client.update(vector_store)
    return store


@router.delete("/")
async def delete_vector_store(
        vector_store:  DeleteVectorStore,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token)
) -> VectorStoreDeleted:
    openai_vector_stores_client = get_openai().openai_vector_stores
    store = await openai_vector_stores_client.delete(vector_store)
    return store
