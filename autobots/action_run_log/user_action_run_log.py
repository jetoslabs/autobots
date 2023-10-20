from typing import List

from fastapi import HTTPException
from pymongo.database import Database

from autobots.action_run_log.action_run_log_crud import ActionRunLogCRUD
from autobots.action_run_log.action_run_log_doc_model import ActionRunLogDoc, ActionRunLogDocFind, ActionRunLogFind, \
    ActionRunLog
from autobots.core.log import log
from autobots.user.user_orm_model import UserORM


class UserActionRunLog:

    def __init__(self, user: UserORM,  db: Database):
        self.user = user
        self.user_id = str(user.id)
        self.action_run_log_crud = ActionRunLogCRUD(db)

    async def create_action_run_log(self, action_run_log: ActionRunLog) -> ActionRunLogDoc | None:
        try:
            action_run_log_doc = await self.action_run_log_crud.insert_one(action_run_log)
            return action_run_log_doc
        except Exception as e:
            log.error(e)
        return None

    async def list_action_run_log(
            self, action_run_log_find: ActionRunLogFind,
            limit: int = 100, offset: int = 0
    ) -> List[ActionRunLogDoc]:
        action_run_log_doc_find = ActionRunLogDocFind(action_user_id=self.user_id, **action_run_log_find.model_dump())
        action_run_log_docs = await self.action_run_log_crud.find(action_run_log_doc_find, limit, offset)
        return action_run_log_docs

    async def get_action_run_log(
            self, action_run_log_id: str
    ) -> ActionRunLogDoc | None:
        try:
            action_run_log_doc_find = ActionRunLogDocFind(action_id=action_run_log_id, action_user_id=self.user_id)
            action_run_log_docs = await self.action_run_log_crud.find(action_run_log_doc_find)
            if len(action_run_log_docs) != 1:
                raise HTTPException(500, "Error in finding action_run_log")
            return action_run_log_docs[0]
        except Exception as e:
            log.error(e)
        return None

    # async def update_action(
    #         self, action_id: str, action_update: ActionUpdate, db: Database = Depends(get_mongo_db)
    # ) -> ActionDoc:
    #     action_doc_update = ActionDocUpdate(id=action_id, user_id=self.user_id, **action_update.model_dump())
    #     action_doc = await ActionCRUD(db).update_one(action_doc_update)
    #     return action_doc

    async def delete_action_run_log(
            self, action_id: str
    ) -> int:
        action_run_log_doc_find = ActionRunLogDocFind(action_id=action_id, action_user_id=self.user_id)
        delete_result = await self.action_run_log_crud.delete_many(action_run_log_doc_find)
        return delete_result.deleted_count
