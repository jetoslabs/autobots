from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.core.database.mongo_base_crud import CRUDBase
from src.autobots.event_result.event_result_model import EventResultDoc, EventResultDocCreate, EventResultDocFind, \
    EventResultDocUpdate


class EventResultCRUD(CRUDBase[EventResultDoc, EventResultDocCreate, EventResultDocFind, EventResultDocUpdate]):

    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
        document: AsyncIOMotorCollection = db[EventResultDoc.__collection__]
        super().__init__(EventResultDoc, document)

