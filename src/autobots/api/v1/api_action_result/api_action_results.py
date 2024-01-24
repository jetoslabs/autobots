from typing import List
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from src.autobots import SettingsProvider
from src.autobots.action.action_result.action_result_doc_model import ActionResultDoc
from src.autobots.action.action_result.user_action_result import UserActionResult
from src.autobots.auth.security import get_user_from_access_token
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.event_result.event_result_model import EventResultFind, EventResultStatus
from src.autobots.user.user_orm_model import UserORM

router = APIRouter(prefix=SettingsProvider.sget().API_ACTION_RESULTS, tags=[SettingsProvider.sget().API_ACTION_RESULTS])


# @router.post("/")
# async def create_action_result(
#         action_doc: ActionDoc,
#         user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
#         db: Database = Depends(get_mongo_db)
# ) -> ActionResultDoc:
#     user_orm = UserORM(id=UUID(user_res.user.id))
#     action_result = ActionResultCreate(status=EventResultStatus.processing, result=action_doc)
#     action_result_doc = await UserActionResult(user_orm, db).create_action_result(action_result)
#     return action_result_doc


@router.get("/")
async def list_action_result(
        id: str = None, status: EventResultStatus = None, is_saved: bool = None,
        #action_id: str = None, action_name: str = None, action_version: float = None, action_type: ActionType = None,
        limit: int = 100, offset: int = 0,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> List[ActionResultDoc]:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_action_result = UserActionResult(user_orm, db)
    action_result_find = EventResultFind(
        id=id, status=status, is_saved=is_saved,
        # result={"id": action_id, "name": action_name, "version": action_version, "type": action_type},
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
