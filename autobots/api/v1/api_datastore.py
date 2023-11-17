from typing import Annotated, List
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import HttpUrl
from sqlalchemy.orm import Session

from autobots.auth.security import get_user_from_access_token
from autobots.core.log import log
from autobots.database.base import get_db
from autobots.datastore.user_datastore import UserDatastore
from autobots.prompts.user_prompts import TextObj
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
        log.exception(str(e))
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
        log.exception(str(e))
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
        log.exception(str(e))
        raise HTTPException(500, "unable to get datastore")


@router.post("/{id}/store_text")
async def store_text(
        id: str,
        text: TextObj,
        chunk_token_size: int = 512,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Session = Depends(get_db)
):
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        user_datastore = await UserDatastore(user_orm, db).hydrate(id)
        await user_datastore.put_data(data=text.text, chunk_token_size=chunk_token_size)
        return {"done": "ok"}
    except Exception as e:
        log.exception(str(e))
        raise HTTPException(500, "unable to get datastore")


@router.post("/{id}/store_file")
async def upload_files(
        id: str,
        files: Annotated[list[UploadFile], File(description="Multiple files as UploadFile")],
        chunk_size: int = 500,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Session = Depends(get_db)
):
    user = UserORM(id=UUID(user_res.user.id))
    user_datastore = await UserDatastore(user, db).hydrate(id)
    await user_datastore.put_files(files, chunk_size=chunk_size)
    return {"done": "ok"}


@router.post("/{id}/store_urls")
async def store_urls(
        id: str,
        urls: List[HttpUrl],
        chunk_token_size: int = 512,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Session = Depends(get_db)
):
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        user_datastore = await UserDatastore(user_orm, db).hydrate(id)
        await user_datastore.put_urls(urls=urls, chunk_token_size=chunk_token_size)
        return {"done": "ok"}
    except Exception as e:
        log.exception(str(e))
        raise HTTPException(500, "unable to get datastore")


@router.post("/{id}/search")
async def search(
        id: str,
        query: TextObj,
        top_k: int = 10,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Session = Depends(get_db)
):
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        user_datastore = await UserDatastore(user_orm, db).hydrate(id)
        results = await user_datastore.search(query=query.text, top_k=top_k)
        return results
    except Exception as e:
        log.exception(str(e))
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
        log.exception(str(e))
        raise HTTPException(500, "unable to delete datastore")
