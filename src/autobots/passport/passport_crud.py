from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.core.database.mongo_base_crud import CRUDBase
from src.autobots.passport.passport_doc_model import APIKeyDoc, APIKeyCreate, APIKeyFind

class APIKeyCRUD(
    CRUDBase[APIKeyDoc, APIKeyDoc, APIKeyCreate, APIKeyFind]
):

    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
        self.document: AsyncIOMotorCollection = db[APIKeyDoc.__collection__]
        super().__init__(APIKeyDoc, APIKeyDoc, self.document)