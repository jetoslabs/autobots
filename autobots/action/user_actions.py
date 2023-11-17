from typing import List, Any

import requests
from fastapi import Depends, HTTPException
from pydantic import HttpUrl
from pymongo.database import Database

from autobots.action.action_crud import ActionCRUD
from autobots.action.action_doc_model import ActionFind, ActionDocFind, ActionDoc, ActionDocCreate, ActionCreate, \
    ActionUpdate, ActionDocUpdate
from autobots.action.action_manager import ActionManager
from autobots.action_result.action_result_doc_model import ActionResultDoc, ActionResult
from autobots.action_result.user_action_result import UserActionResult
from autobots.core.log import log
from autobots.database.mongo_base import get_mongo_db
from autobots.prompts.user_prompts import TextObj
from autobots.user.user_orm_model import UserORM


class UserActions:

    def __init__(self, user: UserORM):
        self.user = user
        self.user_id = str(user.id)

    async def create_action(
            self, action_create: ActionCreate, db: Database = Depends(get_mongo_db)
    ) -> ActionDoc | None:
        try:
            action_doc_create = ActionDocCreate(user_id=self.user_id, **action_create.model_dump())
            action_doc = await ActionCRUD(db).insert_one(action_doc_create)
            return action_doc
        except Exception as e:
            log.exception(str(e))
        return None

    async def list_actions(
            self, action_find: ActionFind,
            db: Database = Depends(get_mongo_db),
            limit: int = 100, offset: int = 0
    ) -> List[ActionDoc]:
        action_doc_find = ActionDocFind(user_id=self.user_id, **action_find.model_dump())
        action_docs = await ActionCRUD(db).find(action_doc_find, limit, offset)
        return action_docs

    async def get_action(
            self, action_id: str, db: Database = Depends(get_mongo_db)
    ) -> ActionDoc | None:
        try:
            action_doc_find = ActionDocFind(id=action_id, user_id=self.user_id)
            action_docs = await ActionCRUD(db).find(action_doc_find)
            if len(action_docs) != 1:
                raise HTTPException(500, "Error in finding action")
            return action_docs[0]
        except Exception as e:
            log.exception(str(e))
        return None

    async def update_action(
            self, action_id: str, action_update: ActionUpdate, db: Database = Depends(get_mongo_db)
    ) -> ActionDoc:
        action_doc_update = ActionDocUpdate(id=action_id, user_id=self.user_id, **action_update.model_dump())
        action_doc = await ActionCRUD(db).update_one(action_doc_update)
        return action_doc

    async def delete_action(
            self, action_id: str, db: Database = Depends(get_mongo_db)
    ) -> int:
        action_doc_find = ActionDocFind(id=action_id, user_id=self.user_id)
        delete_result = await ActionCRUD(db).delete_many(action_doc_find)
        return delete_result.deleted_count

    async def run_action(
            self, action_id: str, input: TextObj, db: Database = Depends(get_mongo_db)
    ) -> Any:
        action_doc_find = ActionDocFind(id=action_id, user_id=self.user_id)
        action_docs = await ActionCRUD(db).find(action_doc_find)
        if len(action_docs) != 1:
            raise HTTPException(405, "Action cannot be run")
        resp = await ActionManager().run_action(action_docs[0], input)
        return resp

    async def run_action_in_background(
            self,
            action_id: str,
            input: TextObj,
            user_action_result: UserActionResult,
            action_result_doc: ActionResultDoc,
            db: Database = Depends(get_mongo_db),
            webhook: HttpUrl = None,
    ) -> None:
        action_doc_find = ActionDocFind(id=action_id, user_id=self.user_id)
        action_docs = await ActionCRUD(db).find(action_doc_find)
        if len(action_docs) != 1:
            raise HTTPException(405, "Action cannot be run")

        resp = await ActionManager().run_action(action_docs[0], input)

        action_result_doc.action.output = resp
        action_result_update = ActionResult(action=action_result_doc.action)
        action_result_doc = await user_action_result.update_action_result(action_result_doc.id, action_result_update)
        log.info(action_result_doc)
        if webhook:
            try:
                with requests.Session() as session:
                    session.post(url=webhook, json=action_result_doc.model_dump_json(), timeout=5)
            except Exception as e:
                # Acceptable as we dont want to wait for webhook response
                pass



    @staticmethod
    async def test_action(action_doc: ActionDoc, input: TextObj) -> Any:
        resp = await ActionManager().run_action(action_doc, input)
        return resp
