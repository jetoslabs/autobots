from typing import Any, Mapping
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette import status

from src.autobots import SettingsProvider
from src.autobots.auth.security import get_user_from_access_token
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.core.database.mongo_base_crud import DocFindPage
from src.autobots.data_model.context import Context
from src.autobots.exception.app_exception import AppException
from src.autobots.secret.app_auth.app_auth_factory import AppAuthFactory
from src.autobots.secret.app_auth.app_auth_model import AppAuthSecretCreate, AppAuthSecretFind, AppAuthSecretUpdate, \
    OptionalAppAuthSecret
from src.autobots.secret.app_auth.app_auth_secret_crud import AppAuthSecretCRUD
from src.autobots.secret.app_auth.app_auths_enum import APP_AUTHS
from src.autobots.secret.app_auth.user_app_auth_secret_handler import UserAppAuthSecretHandler
from src.autobots.secret.user_secret_model import UserSecretDoc
from src.autobots.user.user_orm_model import UserORM

router = APIRouter(prefix=SettingsProvider.sget().API_SECRETS, tags=[SettingsProvider.sget().API_SECRETS])


@router.get("/apps")
async def list_apps(
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
):
    apps = APP_AUTHS.list()
    return apps


@router.get("/apps/{app}")
async def get_app_data_types(
        app: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
):
    ctx = Context()
    app_data_type = await AppAuthFactory.get_data_type(ctx=ctx, app=app)

    return app_data_type.model_json_schema()


@router.post("/")
async def create_api_auth_secret(
        secret_create: AppAuthSecretCreate,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> UserSecretDoc:
    ctx = Context()
    user_orm = UserORM(id=UUID(user_res.user.id))
    crud = AppAuthSecretCRUD(db)
    doc = await UserAppAuthSecretHandler.create(
        ctx=ctx,
        user=user_orm,
        crud=crud,
        app_auth_create=secret_create,
    )
    match doc:
        case UserSecretDoc():
            return doc
        case HTTPException():
            raise doc
        case AppException():
            raise HTTPException(status_code=doc.http_status, detail=f"Secret Not Created, {doc.detail}")
        case _:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Secret Not Created, ")


@router.get("/")
async def list_api_auth_secrets(
        id: str | None = None, app: str | None = None,
        limit: int = 100, offset: int = 0,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> DocFindPage:
    ctx = Context()
    user_orm = UserORM(id=UUID(user_res.user.id))
    crud = AppAuthSecretCRUD(db)
    app_auth_find = AppAuthSecretFind(id=id, secret=OptionalAppAuthSecret(app=app))
    doc_page = await UserAppAuthSecretHandler.find(
        ctx=ctx,
        user=user_orm,
        crud=crud,
        app_auth_find=app_auth_find,
        limit=limit,
        offset=offset,
    )
    return doc_page


@router.get("/{id}")
async def get_api_auth_secret(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> UserSecretDoc:
    ctx = Context()
    user_orm = UserORM(id=UUID(user_res.user.id))
    crud = AppAuthSecretCRUD(db)
    app_auth_find = AppAuthSecretFind(id=id)
    doc = await UserAppAuthSecretHandler.read(
        ctx=ctx,
        user=user_orm,
        crud=crud,
        app_auth_find=app_auth_find
    )
    match doc:
        case None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret Not Found")
        case _:
            return doc


@router.put("/{id}")
async def update_api_auth_secret(
        id: str,
        app_auth_update: AppAuthSecretUpdate,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> UserSecretDoc:
    ctx = Context()
    user_orm = UserORM(id=UUID(user_res.user.id))
    crud = AppAuthSecretCRUD(db)
    assert id == app_auth_update.id
    doc = await UserAppAuthSecretHandler.update(
        ctx=ctx,
        user=user_orm,
        crud=crud,
        app_auth_update=app_auth_update,
    )
    match doc:
        case None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret Not Updated")
        case _:
            return doc


@router.delete("/{id}")
async def delete_api_auth_secrets(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> Mapping[str, Any]:
    ctx = Context()
    user_orm = UserORM(id=UUID(user_res.user.id))
    crud = AppAuthSecretCRUD(db)
    app_auth_find = AppAuthSecretFind(id=id)
    doc = await UserAppAuthSecretHandler.delete(
        ctx=ctx,
        user=user_orm,
        crud=crud,
        app_auth_find=app_auth_find,
    )
    match doc:
        case Exception():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret Not Deleted")
        case _:
            return doc.raw_result


@router.post("/{id}/api-header")
async def create_api_header(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> UserSecretDoc:
    ctx = Context()
    user_orm = UserORM(id=UUID(user_res.user.id))
    crud = AppAuthSecretCRUD(db)
    app_auth_find = AppAuthSecretFind(id=id)
    doc = await UserAppAuthSecretHandler.update_auth_header(ctx=ctx, user=user_orm, crud=crud,
                                                            app_auth_find=app_auth_find)
    match doc:
        case Exception():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Secret Not Updated")
        case _:
            return doc
