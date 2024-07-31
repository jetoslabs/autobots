from typing import List
from fastapi import HTTPException
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.autobots.action.action_chat.chat_doc_model import ChatDoc
from src.autobots.user.user_orm_model import UserORM
from src.autobots.data_model.context import Context
from src.autobots.poll_graph.poll_graph import PollDoc, PollCreate, PollUpdate, PollFind
from src.autobots.poll_graph.poll_graph_crud import PollCRUD


class UserPollGraph:
    """
    User Poll Graph manages polls created by users and their interactions.
    """
    DEFAULT_TITLE = "New Poll"

    def __init__(self, user: UserORM, db: AsyncIOMotorDatabase):
        self.user = user
        self.user_id = str(user.id)
        self.poll_crud = PollCRUD(db)

    async def create_poll(self, poll_create: PollCreate, title: str = DEFAULT_TITLE) -> PollDoc | None:
        try:
            poll_doc_create = PollCreate(user_id=self.user_id, title=title, **poll_create.model_dump(by_alias=True))
            poll_doc = await self.poll_crud.insert_one(poll_doc_create)
            return poll_doc
        except Exception as e:
            logger.error(str(e))
        return None

    async def list_polls(self, limit: int = 100, offset: int = 0) -> List[PollDoc] | None:
        try:
            poll_docs = await self.poll_crud.find({"user_id": self.user_id}, limit=limit, offset=offset)
            return poll_docs
        except Exception as e:
            logger.error(str(e))
        return None

    async def get_poll(self, poll_id: str) -> PollDoc | None:
        try:
            poll_doc = await self.poll_crud.find_one({"id": poll_id, "user_id": self.user_id})
            if not poll_doc:
                raise HTTPException(404, "Poll not found")
            return poll_doc
        except Exception as e:
            logger.error(str(e))
        return None

    async def update_poll(self, poll_id: str, poll_update: PollUpdate) -> PollDoc:
        poll_doc_update = PollUpdate(id=poll_id, user_id=self.user_id, **poll_update.model_dump())
        poll_doc = await self.poll_crud.update_one(poll_doc_update)
        return poll_doc

    async def delete_poll(self, poll_id: str):
        delete_result = await self.poll_crud.delete_many({"id": poll_id, "user_id": self.user_id})
        return delete_result.deleted_count
