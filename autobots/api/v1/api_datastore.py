from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from autobots.auth.security import get_user_from_access_token
from autobots.core.log import log
from autobots.database.base import get_db
from autobots.datastore.user_datastore import UserDatastore
from autobots.prompts.user_prompts import Input
from autobots.user.user_orm_model import UserORM

router = APIRouter()


@router.post("/")
async def create_datastore(
        name: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Session = Depends(get_db)
):
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        user_datastore_meta = await UserDatastore(user_orm, db).init(name)
        return user_datastore_meta
    except Exception as e:
        log.error(e)
        raise HTTPException(500, "unable to create datastore")


@router.get("/")
async def list_datastore(
        limit: int = 100, offset: int = 0,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Session = Depends(get_db)
):
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        user_datastore_meta = await UserDatastore(user_orm, db).list(db, limit, offset)
        return user_datastore_meta
    except Exception as e:
        log.error(e)
        raise HTTPException(500, "unable to list datastore")


@router.get("/{name}")
async def get_datastore(
        name: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Session = Depends(get_db)
):
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        user_datastore_meta = await UserDatastore(user_orm, db).get(name)
        return user_datastore_meta
    except Exception as e:
        log.error(e)
        raise HTTPException(500, "unable to get datastore")


@router.post("/{id}/store")
async def store_text(
        id: str,
        text: Input,
        chunk_token_size: int = 512,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Session = Depends(get_db)
):
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        user_datastore = await UserDatastore(user_orm, db).hydrate(id)
        await user_datastore.put_data(data=text.input, chunk_token_size=chunk_token_size)
        return {"done": "ok"}
    except Exception as e:
        log.error(e)
        raise HTTPException(500, "unable to get datastore")


@router.post("/{id}/search")
async def search(
        id: str,
        query: Input,
        top_k: int = 10,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Session = Depends(get_db)
):
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        user_datastore = await UserDatastore(user_orm, db).hydrate(id)
        results = await user_datastore.search(query=query.input, top_k=top_k)
        return results
    except Exception as e:
        log.error(e)
        raise HTTPException(500, "unable to get datastore")


@router.delete("/{id}")
async def delete_datastore(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Session = Depends(get_db)
):
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        user_datastore_meta = await UserDatastore(user_orm, db).delete(db, id)
        return user_datastore_meta
    except Exception as e:
        log.error(e)
        raise HTTPException(500, "unable to delete datastore")