from typing import List, Any, Dict
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from autobots.action.action_doc_model import ActionDoc, ActionFind, ActionUpdate
from autobots.action.action_manager import ActionManager
from autobots.action.action_type.action_types import ActionType
from autobots.action.user_actions import UserActions
from autobots.auth.security import get_user_from_access_token
from autobots.database.mongo_base import get_mongo_db
from autobots.user.user_orm_model import UserORM

router = APIRouter()


@router.get("/types")
async def get_action_types(
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token)
) -> List[str]:
    return ActionManager.get_action_types()


@router.get("/")
async def list_actions(
        id: str = None, name: str = None, version: float = None, type: ActionType = None, is_published: bool = None,
        limit: int = 100, offset: int = 0,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> List[ActionDoc]:
    user_orm = UserORM(id=UUID(user_res.user.id))
    action_find = ActionFind(id=id, name=name, version=version, type=type, is_published=is_published)
    action_docs = await UserActions(user=user_orm, db=db).list_actions(action_find, limit, offset)
    return action_docs


@router.get("/{id}")
async def get_action(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    action_doc = await UserActions(user=user_orm, db=db).get_action(id)
    return action_doc


@router.put("/{id}")
async def update_action(
        id: str,
        action_update: ActionUpdate,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    action_doc = await UserActions(user=user_orm, db=db).update_action(id, action_update)
    return action_doc


@router.delete("/{id}")
async def delete_action(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_actions = UserActions(user=user_orm, db=db)
    action_doc = await user_actions.get_action(id)
    if action_doc is None:
        raise HTTPException(400, "Action not found")
    deleted_count = await user_actions.delete_action(id)
    if deleted_count != 1:
        raise HTTPException(500, "Error in deleting action")
    return action_doc


@router.post("/{id}/run")
async def run_action(
        id: str,
        input: Dict[str, Any],
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> Any:
    user_orm = UserORM(id=UUID(user_res.user.id))
    resp = await UserActions(user=user_orm, db=db).run_action(id, input)
    return resp

