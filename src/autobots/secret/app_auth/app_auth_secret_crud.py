from fastapi import Depends
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from overrides import overrides
from pydantic import HttpUrl

from src.autobots.exception.app_exception import AppException
from src.autobots.secret.app_auth.app_auth_model import UserAppAuthSecretDocCreate, UserAppAuthSecretDocFind, \
    UserAppAuthSecretDocUpdate, OptionalAppAuthSecret
from src.autobots.secret.user_secret_model import UserSecretDoc
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.core.database.mongo_base_crud import CRUDBase


class AppAuthSecretCRUD(
    CRUDBase[
        UserSecretDoc,
        UserSecretDoc,
        UserAppAuthSecretDocCreate,
        UserAppAuthSecretDocFind,
        UserAppAuthSecretDocUpdate
    ]
):

    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
        self.document: AsyncIOMotorCollection = db[UserSecretDoc.__collection__]
        super().__init__(UserSecretDoc, UserSecretDoc, self.document)

    @overrides
    async def insert_one(self, create_doc: UserAppAuthSecretDocCreate) -> UserSecretDoc | Exception:
        try:
            http_url = HttpUrl(create_doc.secret.api_domain)
            api_domain = f"{http_url.scheme}://{http_url.host}"
            doc_find = UserAppAuthSecretDocFind(
                user_id=create_doc.user_id,
                secret=OptionalAppAuthSecret(api_domain=api_domain)
            )
            existing_result = await self.find_one(doc_find=doc_find)
            if existing_result:
                logger.bind(create_doc=create_doc).info("Secret with this api_domain already exists")
                return AppException(detail="Secret with this api_domain already exists", http_status=409)
            insert_result = await self.document.insert_one(create_doc.model_dump())
            inserted_result = await self._find_by_id(insert_result.inserted_id)
            return inserted_result
        except Exception as e:
            logger.bind(create_doc=create_doc).error(str(e))
            return e
