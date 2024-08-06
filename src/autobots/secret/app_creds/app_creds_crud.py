from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.core.database.mongo_base_crud import CRUDBase
from src.autobots.secret.app_creds.app_creds_model import AppCredsDoc, AppCredsLiteDoc, AppCredsDocCreate, \
    AppCredsDocRead, AppCredsDocUpdate


class AppCredsCRUD(CRUDBase[AppCredsDoc, AppCredsLiteDoc, AppCredsDocCreate, AppCredsDocRead, AppCredsDocUpdate]):

    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
        document: AsyncIOMotorCollection = db[AppCredsDoc.__collection__]
        super().__init__(AppCredsDoc, AppCredsLiteDoc, document)
