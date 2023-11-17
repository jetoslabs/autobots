from typing import List

from fastapi import HTTPException
from pymongo.database import Database

from autobots.action_result.action_result_crud import ActionResultCRUD
from autobots.action_result.action_result_doc_model import ActionResultDoc, ActionResultDocFind, ActionResultFind, \
    ActionResult, ActionResultDocUpdate
from autobots.core.log import log
from autobots.user.user_orm_model import UserORM


class UserActionResult:

    def __init__(self, user: UserORM,  db: Database):
        self.user = user
        self.user_id = str(user.id)
        self.action_result_crud = ActionResultCRUD(db)

    async def create_action_result(self, action_result: ActionResult) -> ActionResultDoc | None:
        try:
            action_result_doc = await self.action_result_crud.insert_one(action_result)
            return action_result_doc
        except Exception as e:
            log.exception(str(e))
        return None

    async def list_action_result(
            self, action_result_find: ActionResultFind,
            limit: int = 100, offset: int = 0
    ) -> List[ActionResultDoc]:
        action_result_doc_find = ActionResultDocFind(action_user_id=self.user_id, **action_result_find.model_dump())
        action_result_docs = await self.action_result_crud.find(action_result_doc_find, limit, offset)
        return action_result_docs

    async def get_action_result(
            self, action_result_id: str
    ) -> ActionResultDoc | None:
        try:
            action_result_doc_find = ActionResultDocFind(id=action_result_id, action_user_id=self.user_id)
            action_result_docs = await self.action_result_crud.find(action_result_doc_find)
            if len(action_result_docs) != 1:
                raise HTTPException(500, "Error in finding action_result")
            return action_result_docs[0]
        except Exception as e:
            log.exception(str(e))
        return None

    async def update_action_result(
            self, action_id: str, action_update: ActionResult
    ) -> ActionResultDoc:
        action_doc_update = ActionResultDocUpdate(id=action_id, user_id=self.user_id, **action_update.model_dump())
        action_doc = await self.action_result_crud.update_one(action_doc_update)
        return action_doc

    async def delete_action_result(
            self, action_id: str
    ) -> int:
        action_result_doc_find = ActionResultDocFind(action_id=action_id, action_user_id=self.user_id)
        delete_result = await self.action_result_crud.delete_many(action_result_doc_find)
        return delete_result.deleted_count
