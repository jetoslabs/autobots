from typing import List, Any, Dict

from fastapi import HTTPException
from pymongo.database import Database

from autobots.action.action.action_crud import ActionCRUD
from autobots.action.action.action_doc_model import ActionFind, ActionDocFind, ActionDoc, ActionDocCreate, ActionCreate, \
    ActionUpdate, ActionDocUpdate
from autobots.action.action_type.action_factory import ActionFactory
from autobots.core.logging.log import Log
from autobots.user.user_orm_model import UserORM


class UserActions:

    def __init__(self, user: UserORM, db: Database):
        self.user = user
        self.user_id = str(user.id)
        self.action_crud = ActionCRUD(db)

    async def create_action(
            self, action_create: ActionCreate
    ) -> ActionDoc | None:
        try:
            action_doc_create = ActionDocCreate(user_id=self.user_id, **action_create.model_dump())
            action_doc = await self.action_crud.insert_one(action_doc_create)
            return action_doc
        except Exception as e:
            Log.exception(str(e))
        return None

    async def list_actions(
            self, action_find: ActionFind,
            limit: int = 100, offset: int = 0
    ) -> List[ActionDoc]:
        action_doc_find = ActionDocFind(user_id=self.user_id, **action_find.model_dump())
        action_docs = await self.action_crud.find(action_doc_find, limit, offset)
        return action_docs

    async def get_action(
            self, action_id: str
    ) -> ActionDoc | None:
        try:
            action_doc_find = ActionDocFind(id=action_id, user_id=self.user_id)
            action_docs = await self.action_crud.find(action_doc_find)
            if len(action_docs) != 1:
                raise HTTPException(500, "Error in finding action")
            return action_docs[0]
        except Exception as e:
            Log.exception(str(e))
        return None

    async def update_action(
            self, action_id: str, action_update: ActionUpdate
    ) -> ActionDoc:
        action_doc_update = ActionDocUpdate(id=action_id, user_id=self.user_id, **action_update.model_dump())
        action_doc = await self.action_crud.update_one(action_doc_update)
        return action_doc

    async def delete_action(
            self, action_id: str
    ) -> int:
        action_doc_find = ActionDocFind(id=action_id, user_id=self.user_id)
        delete_result = await self.action_crud.delete_many(action_doc_find)
        return delete_result.deleted_count

    async def run_action(
            self, action_id: str, input: Dict[str, Any]
    ) -> Any:
        action_doc_find = ActionDocFind(id=action_id, user_id=self.user_id)
        action_docs = await self.action_crud.find(action_doc_find)
        if len(action_docs) != 1:
            raise HTTPException(405, "Action cannot be run")
        resp = await ActionFactory().run_action(action_docs[0], input)
        return resp

    async def run_action_v1(
            self, action_id: str, input: Dict[str, Any]
    ) -> ActionDoc:
        action_doc_find = ActionDocFind(id=action_id, user_id=self.user_id)
        action_docs = await self.action_crud.find(action_doc_find)
        if len(action_docs) != 1:
            raise HTTPException(405, "Action not found")
        action_doc = action_docs[0]
        action_doc.input = input
        resp = await ActionFactory().run_action(action_doc, input)
        action_doc.output = resp
        return action_doc

    @staticmethod
    async def run_action_doc(action_doc: ActionDoc, input: Any) -> Any:
        resp = await ActionFactory().run_action(action_doc, input)
        return resp
