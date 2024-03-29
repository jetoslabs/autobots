from fastapi import Depends
from pymongo.collection import Collection
from pymongo.database import Database

from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.core.database.mongo_base_crud import CRUDBase
from src.autobots.event_result.event_result_model import EventResultDoc, EventResultDocCreate, EventResultDocFind, \
    EventResultDocUpdate


class EventResultCRUD(CRUDBase[EventResultDoc, EventResultDocCreate, EventResultDocFind, EventResultDocUpdate]):

    def __init__(self, db: Database = Depends(get_mongo_db)):
        document: Collection = db[EventResultDoc.__collection__]
        super().__init__(EventResultDoc, document)

