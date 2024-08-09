from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.core.database.mongo_base_crud import CRUDBase
from src.autobots.poll_graph.poll_graph import PollDoc, PollCreate, PollFind, PollUpdate

class PollCRUD(
    CRUDBase[PollDoc, PollDoc, PollCreate, PollFind, PollUpdate]
):

    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
        self.document: AsyncIOMotorCollection = db[PollDoc.__collection__]
        super().__init__(PollDoc, PollDoc, self.document)