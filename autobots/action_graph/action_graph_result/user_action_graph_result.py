from typing import List

from fastapi import HTTPException
from pymongo.database import Database

from autobots.action_graph.action_graph_result.action_graph_result_model_doc import ActionGraphResultDoc, \
    ActionGraphResultCreate, ActionGraphResultUpdate
from autobots.core.log import log
from autobots.event_result.event_result_crud import EventResultCRUD
from autobots.event_result.event_result_model import EventResultDocCreate, EventResultFind, EventResultDocFind, \
    EventResultDocUpdate
from autobots.user.user_orm_model import UserORM


class UserActionGraphResult:

    def __init__(self, user: UserORM,  db: Database):
        self.user = user
        self.user_id = str(user.id)
        self.event_result_crud = EventResultCRUD(db)

    async def create_action_graph_result(self, action_graph_result:  ActionGraphResultCreate) -> ActionGraphResultDoc | None:
        try:
            event_result_doc_create = EventResultDocCreate(user_id=self.user_id, **action_graph_result.model_dump())
            event_result_doc = await self.event_result_crud.insert_one(event_result_doc_create)
            action_result_doc = ActionGraphResultDoc.model_validate(event_result_doc.model_dump())
            return action_result_doc
        except Exception as e:
            log.error(e)
            raise e

    async def list_action_graph_result(
            self, action_graph_result_find: EventResultFind,
            limit: int = 100, offset: int = 0
    ) -> List[ActionGraphResultDoc]:
        event_result_doc_find = EventResultDocFind(user_id=self.user_id, **action_graph_result_find.model_dump())
        event_result_docs = await self.event_result_crud.find(event_result_doc_find, limit, offset)
        action_graph_result_docs = []
        for event_result_doc in event_result_docs:
            action_graph_result_doc = ActionGraphResultDoc.model_validate(event_result_doc.model_dump())
            action_graph_result_docs.append(action_graph_result_doc)
        return action_graph_result_docs

    async def get_action_graph_result(
            self, action_result_id: str
    ) -> ActionGraphResultDoc | None:
        try:
            event_result_doc_find = EventResultDocFind(id=action_result_id, user_id=self.user_id)
            event_result_docs = await self.event_result_crud.find(event_result_doc_find)
            if len(event_result_docs) != 1:
                raise HTTPException(500, "Error in finding result")
            event_result_doc = event_result_docs[0]
            action_graph_result_doc = ActionGraphResultDoc.model_validate(event_result_doc.model_dump())
            return action_graph_result_doc
        except Exception as e:
            log.exception(e)
        return None

    async def update_action_graph_result(
            self, action_result_id: str, action_update: ActionGraphResultUpdate
    ) -> ActionGraphResultDoc:
        try:
            event_result_doc_update = EventResultDocUpdate(id=action_result_id, user_id=self.user_id, **action_update.model_dump())
            event_result_doc = await self.event_result_crud.update_one(event_result_doc_update)
            action_graph_result_doc = ActionGraphResultDoc.model_validate(event_result_doc.model_dump())
            return action_graph_result_doc
        except Exception as e:
            log.error(e)
            raise e

    async def delete_action_graph_result(
            self, id: str
    ) -> int:
        event_result_doc_find = EventResultDocFind(id=id, user_id=self.user_id)
        delete_result = await self.event_result_crud.delete_many(event_result_doc_find)
        return delete_result.deleted_count
