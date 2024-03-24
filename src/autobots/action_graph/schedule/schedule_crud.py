from fastapi import Depends
from pymongo.collection import Collection
from pymongo.database import Database

from src.autobots.action_graph.schedule.schedule_doc_model import ScheduleDoc, ScheduleDocCreate, ScheduleDocFind, \
    ScheduleDocUpdate
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.core.database.mongo_base_crud import CRUDBase


class ScheduleCRUD(CRUDBase[ScheduleDoc, ScheduleDocCreate, ScheduleDocFind, ScheduleDocUpdate]):

    def __init__(self, db: Database = Depends(get_mongo_db)):
        document: Collection = db[ScheduleDoc.__collection__]
        super().__init__(ScheduleDoc, document)

