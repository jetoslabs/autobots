from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.results import DeleteResult

from src.autobots.data_model.context import Context
from src.autobots.secret.app_creds.app_creds_crud import AppCredsCRUD
from src.autobots.secret.app_creds.app_creds_model import AppCredsDoc, AppCredsCreate, AppCredsRead, AppCredsUpdate, AppCredsDocCreate, AppCredsDocUpdate, AppCredsDocRead, AppCredsLiteDocPage
from src.autobots.user.user_orm_model import UserORM


class UserAppCreds:

    # Does User level isolation
    # params common in all functions: user: UserORM, db: AsyncIOMotorDatabase

    @staticmethod
    async def create_app_creds(
            ctx: Context, db: AsyncIOMotorDatabase, user: UserORM, app_creds_create: AppCredsCreate
    ) -> AppCredsDoc | None:
        crud = AppCredsCRUD(db=db)
        create_doc = AppCredsDocCreate(user_id=str(user.id), **app_creds_create.model_dump(exclude_none=True))
        doc = await crud.insert_one(create_doc)
        match doc:
            case AppCredsDoc():
                return AppCredsDoc.model_validate(doc)
            case _:
                logger.bind(ctx=ctx, error=str(doc)).error("Cannot create app creds")
        return None

    @staticmethod
    async def list_app_creds(
            ctx: Context, db: AsyncIOMotorDatabase, user: UserORM, app_creds_list: AppCredsRead,
            limit: int = 100, offset: int = 0
    ) -> AppCredsLiteDocPage:
        crud = AppCredsCRUD(db=db)
        find_doc = AppCredsDocRead(user_id=str(user.id), **app_creds_list.model_dump(exclude_none=True))
        page = await crud.find_page(doc_find=find_doc, limit=limit, offset=offset)
        app_creds_page = AppCredsLiteDocPage.model_validate(page)
        return app_creds_page

    @staticmethod
    async def get_app_creds(
            ctx: Context, db: AsyncIOMotorDatabase, user: UserORM, app_creds_id: str
    ) -> AppCredsDoc | None:
        crud = AppCredsCRUD(db=db)
        doc_find = AppCredsDocRead(user_id=str(user.id), id=app_creds_id)
        doc = await crud.find_one(doc_find=doc_find)
        return AppCredsDoc.model_validate(doc) if doc else None

    @staticmethod
    async def update_app_creds(
            ctx: Context, db: AsyncIOMotorDatabase, user: UserORM, app_creds_update: AppCredsUpdate
    ) -> AppCredsDoc | None:
        crud = AppCredsCRUD(db=db)
        doc_update = AppCredsDocUpdate(user_id=str(user.id), **app_creds_update.model_dump(exclude_none=True))
        doc = await crud.update_one(doc_update=doc_update)
        match doc:
            case AppCredsDoc():
                return AppCredsDoc.model_validate(doc)
            case _:
                logger.bind(ctx=ctx, error=str(doc)).error("Cannot update app creds")
        return None

    @staticmethod
    async def delete_app_creds(
            ctx: Context, db: AsyncIOMotorDatabase, user: UserORM, app_creds_delete: AppCredsRead
    ) -> int | None:
        crud = AppCredsCRUD(db=db)
        find_doc = AppCredsDocRead(user_id=str(user.id), **app_creds_delete.model_dump(exclude_none=True))
        deleted = await crud.delete_many(doc_find=find_doc)
        match deleted:
            case DeleteResult():
                return deleted.deleted_count
            case Exception():
                logger.bind(ctx=ctx, error=str(deleted)).error("Cannot delete app creds")
        return None
