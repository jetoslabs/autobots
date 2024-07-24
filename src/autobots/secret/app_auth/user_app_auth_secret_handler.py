from loguru import logger
from pymongo.results import DeleteResult

from src.autobots.exception.app_exception import AppException
from src.autobots.secret.app_auth.app_auth_factory import AppAuthFactory
from src.autobots.secret.app_auth.app_auth_model import AppAuthSecret, AppAuthSecretCreate, UserAppAuthSecretDocCreate, \
    UserAppAuthSecretDocFind, AppAuthSecretFind, AppAuthSecretUpdate, UserAppAuthSecretDocUpdate, OptionalAppAuthSecret
from src.autobots.secret.app_auth.app_auth_secret_crud import AppAuthSecretCRUD
from src.autobots.secret.user_secret_model import UserSecretDoc
from src.autobots.core.database.mongo_base_crud import DocFindPage
from src.autobots.data_model.context import Context
from src.autobots.user.user_orm_model import UserORM


class UserAppAuthSecretHandler:

    _CRUD_TYPE = AppAuthSecretCRUD
    _CRUD_CREATE_TYPE = AppAuthSecretCreate
    _CRUD_FIND_TYPE = AppAuthSecretFind
    _CRUD_UPDATE_TYPE = AppAuthSecretUpdate

    @staticmethod
    async def assert_crud_type(crud):
        assert isinstance(crud, UserAppAuthSecretHandler._CRUD_TYPE)

    @staticmethod
    async def assert_crud_create_type(crud):
        assert isinstance(crud, UserAppAuthSecretHandler._CRUD_CREATE_TYPE)

    @staticmethod
    async def assert_crud_find_type(crud):
        assert isinstance(crud, UserAppAuthSecretHandler._CRUD_FIND_TYPE)

    @staticmethod
    async def assert_crud_update_type(crud):
        assert isinstance(crud, UserAppAuthSecretHandler._CRUD_UPDATE_TYPE)

    @staticmethod
    async def create(
            ctx: Context, user: UserORM, crud: AppAuthSecretCRUD, app_auth_create: AppAuthSecretCreate,
    ) -> UserSecretDoc | Exception:
        await UserAppAuthSecretHandler.assert_crud_type(crud)
        await UserAppAuthSecretHandler.assert_crud_create_type(app_auth_create)
        # find if record exist with same app name for user_id
        app_auth_find = AppAuthSecretFind(secret=OptionalAppAuthSecret(app=app_auth_create.secret.app))
        page = await UserAppAuthSecretHandler.find(
            ctx=ctx, user=user, crud=crud, app_auth_find=app_auth_find
        )
        if page.total_count > 0:
            return AppException(detail="App Auth already exists", http_status=400)

        create_doc = UserAppAuthSecretDocCreate(user_id=str(user.id), **app_auth_create.model_dump(exclude_none=True))
        doc = await crud.insert_one(create_doc=create_doc)
        match doc:
            case Exception():
                logger.bind(ctx=ctx, user_id=str(user.id), create_doc=create_doc).error("User auth secret not created")
            case UserSecretDoc():
                logger.bind(ctx=ctx, user_id=str(user.id), doc=doc.model_dump()).info("User auth secret created")
        return doc

    @staticmethod
    async def read(
            ctx: Context, user: UserORM, crud: AppAuthSecretCRUD, app_auth_find: AppAuthSecretFind,
    ) -> UserSecretDoc | None:
        await UserAppAuthSecretHandler.assert_crud_type(crud)
        await UserAppAuthSecretHandler.assert_crud_find_type(app_auth_find)
        find_doc = UserAppAuthSecretDocFind(user_id=str(user.id), **app_auth_find.model_dump(exclude_none=True))
        doc = await crud.find_one(doc_find=find_doc)
        match doc:
            case None:
                logger.bind(ctx=ctx, user_id=str(user.id), find_doc=find_doc).info("User auth secret not found")
            case UserSecretDoc():
                logger.bind(ctx=ctx, user_id=str(user.id), doc=doc.model_dump()).info("User auth secret read")
        return doc

    @staticmethod
    async def find(
            ctx: Context,
            user: UserORM,
            crud: AppAuthSecretCRUD,
            app_auth_find: AppAuthSecretFind,
            limit: int = 100,
            offset: int = 0
    ) -> DocFindPage:
        await UserAppAuthSecretHandler.assert_crud_type(crud)
        await UserAppAuthSecretHandler.assert_crud_find_type(app_auth_find)
        find_doc = UserAppAuthSecretDocFind(user_id=str(user.id), **app_auth_find.model_dump(exclude_none=True))
        page = await crud.find_page(doc_find=find_doc, limit=limit, offset=offset)
        logger.bind(ctx=ctx, user_id=str(user.id), doc=page.model_dump()).info("User auth secret found")
        return page

    @staticmethod
    async def update(
            ctx: Context, user: UserORM, crud: AppAuthSecretCRUD, app_auth_update: AppAuthSecretUpdate
    ) -> UserSecretDoc | Exception:
        await UserAppAuthSecretHandler.assert_crud_type(crud)
        await UserAppAuthSecretHandler.assert_crud_update_type(app_auth_update)
        update_doc = UserAppAuthSecretDocUpdate(user_id=str(user.id), **app_auth_update.model_dump(exclude_none=True))
        doc = await crud.update_one(doc_update=update_doc)
        logger.bind(ctx=ctx, user_id=str(user.id), doc=doc.model_dump()).info("User auth secret updated")
        return doc

    @staticmethod
    async def delete(
            ctx: Context, user: UserORM, crud: AppAuthSecretCRUD, app_auth_find: AppAuthSecretFind,
    ) -> DeleteResult | Exception:
        await UserAppAuthSecretHandler.assert_crud_type(crud)
        await UserAppAuthSecretHandler.assert_crud_find_type(app_auth_find)
        find_doc = UserAppAuthSecretDocFind(user_id=str(user.id), **app_auth_find.model_dump(exclude_none=True))
        doc = await crud.delete_many(doc_find=find_doc)
        match doc:
            case Exception():
                logger.bind(ctx=ctx, user_id=str(user.id), err=str(doc)).error("User auth secret not found")
            case DeleteResult():
                logger.bind(ctx=ctx, user_id=str(user.id), doc=doc.raw_result).info("User auth secret deleted")
        return doc

    @staticmethod
    async def update_auth_header(
            ctx: Context, user: UserORM, crud: AppAuthSecretCRUD, app_auth_find: AppAuthSecretFind,
    ) -> UserSecretDoc | Exception:
        await UserAppAuthSecretHandler.assert_crud_type(crud)
        await UserAppAuthSecretHandler.assert_crud_find_type(app_auth_find)
        user_secret_doc = await UserAppAuthSecretHandler.read(ctx=ctx, user=user, crud=crud, app_auth_find=app_auth_find)
        if user_secret_doc is None:
            return AppException(detail="User secret not found", http_status=404)

        app_auth = AppAuthSecret.model_validate(user_secret_doc.secret)
        updated_app_auth = await AppAuthFactory.update_auth_header(ctx=ctx, app_auth=app_auth)

        update_doc = UserAppAuthSecretDocUpdate(
            id=user_secret_doc.id,
            user_id=str(user.id),
            secret=updated_app_auth.model_dump(exclude_none=True),
        )
        doc = await crud.update_one(doc_update=update_doc)
        logger.bind(ctx=ctx, user_id=str(user.id), doc=doc.model_dump()).info("User auth secret updated")
        return doc
