from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from src.autobots.secret.app_auth.app_auth_model import UserAppAuthSecretDocCreate, UserAppAuthSecretDocFind, \
    UserAppAuthSecretDocUpdate
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
