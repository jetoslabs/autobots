from typing import List
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from autobots import SettingsProvider
from autobots.action.action.action_doc_model import ActionDoc
from autobots.action.action_type.action_types import ActionType
from autobots.action.action_result.action_result_doc_model import ActionResultDoc, ActionResultCreate
from autobots.action.action_result.user_action_result import UserActionResult
from autobots.auth.security import get_user_from_access_token
from autobots.core.database.mongo_base import get_mongo_db
from autobots.event_result.event_result_model import EventResultFind, EventResultStatus
from autobots.user.user_orm_model import UserORM

router = APIRouter(prefix=SettingsProvider.sget().API_ACTION_RESULTS, tags=[SettingsProvider.sget().API_ACTION_RESULTS])


@router.post("/")
async def create_action_result(
        action_doc: ActionDoc,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionResultDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    action_result = ActionResultCreate(status=EventResultStatus.processing, result=action_doc)
    action_result_doc = await UserActionResult(user_orm, db).create_action_result(action_result)
    return action_result_doc


@router.get("/")
async def list_action_result(
        id: str = None, action_id: str = None, action_name: str = None,
        action_version: float = None, action_type: ActionType = None,
        limit: int = 100, offset: int = 0,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> List[ActionResultDoc]:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_action_result = UserActionResult(user_orm, db)
    action_result_find = EventResultFind(
        id=id, action_id=action_id, action_name=action_name,
        action_version=action_version, action_type=action_type
    )
    action_result_docs = await user_action_result.list_action_result(action_result_find, limit, offset)
    return action_result_docs


@router.get("/{id}")
async def get_action_result(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionResultDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    action_result_doc = await UserActionResult(user_orm, db).get_action_result(id)
    return action_result_doc


@router.delete("/{id}")
async def delete_action_result(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionResultDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_action_result = UserActionResult(user_orm, db)
    action_result = await user_action_result.get_action_result(id)
    if not action_result:
        raise HTTPException(404, "Action Result not found")
    deleted = await UserActionResult(user_orm, db).delete_action_result(id)
    if deleted != 1:
        raise HTTPException(500, "Error in deleting Action Result")
    return action_result
