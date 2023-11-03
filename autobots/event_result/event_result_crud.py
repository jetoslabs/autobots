from fastapi import Depends
from pymongo.database import Database

from autobots.core.database.mongo_base import get_mongo_db
from autobots.core.database.mongo_base_crud import CRUDBase
from autobots.event_result.event_result_model import EventResultDoc, EventResultDocCreate, EventResultDocFind, \
    EventResultDocUpdate


class EventResultCRUD(CRUDBase[EventResultDoc, EventResultDocCreate, EventResultDocFind, EventResultDocUpdate]):

    def __init__(self, db: Database = Depends(get_mongo_db)):
        super().__init__(db)

