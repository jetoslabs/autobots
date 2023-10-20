from typing import List
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from autobots.action.action_doc_model import ActionDoc
from autobots.action.action_type.action_types import ActionType
from autobots.action_run_log.action_run_log_doc_model import ActionRunLogDoc, ActionRunLogFind, ActionRunLog
from autobots.action_run_log.user_action_run_log import UserActionRunLog
from autobots.auth.security import get_user_from_access_token
from autobots.database.mongo_base import get_mongo_db
from autobots.user.user_orm_model import UserORM

router = APIRouter()


@router.post("/")
async def create_action_run_log(
        action_doc: ActionDoc,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionRunLogDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    action_run_log = ActionRunLog(action=action_doc)
    action_run_log_doc = await UserActionRunLog(user_orm, db).create_action_run_log(action_run_log)
    return action_run_log_doc


@router.get("/")
async def list_action_run_log(
        id: str = None, action_id: str = None, action_name: str = None,
        action_version: float = None, action_type: ActionType = None,
        limit: int = 100, offset: int = 0,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> List[ActionRunLogDoc]:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_action_run_log = UserActionRunLog(user_orm, db)
    action_run_log_find = ActionRunLogFind(
        id=id, action_id=action_id, action_name=action_name,
        action_version=action_version, action_type=action_type
    )
    action_run_log_docs = await user_action_run_log.list_action_run_log(action_run_log_find, limit, offset)
    return action_run_log_docs


@router.get("/{id}")
async def get_action_run_log(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionRunLogDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    action_market_doc = await UserActionRunLog(user_orm, db).get_action_run_log(id)
    return action_market_doc


@router.delete("/{id}")
async def delete_action_run_log(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionRunLogDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_action_run_log = UserActionRunLog(user_orm, db)
    action_run_log = await user_action_run_log.get_action_run_log(id)
    if not action_run_log:
        raise HTTPException(404, "Action Run Log not found")
    deleted = await UserActionRunLog(user_orm, db).delete_action_run_log(id)
    if deleted != 1:
        raise HTTPException(500, "Error in deleting Action Run Log")
    return action_run_log
