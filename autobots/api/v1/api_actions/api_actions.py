from typing import List, Any
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from autobots.action.action_doc_model import ActionDoc, ActionFind, ActionUpdate
from autobots.action.action_manager import ActionManager
from autobots.action.action_types import ActionType
from autobots.action.user_actions import UserActions
from autobots.auth.security import get_user_from_access_token
from autobots.database.mongo_base import get_mongo_db
from autobots.prompts.user_prompts import TextObj
from autobots.user.user_orm_model import UserORM

router = APIRouter()


@router.get("/types")
async def get_action_types(
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token)
) -> List[str]:
    return ActionManager.get_action_types()


@router.get("/")
async def list_actions(
        id: str = None, name: str = None, version: float = None, type: ActionType = None,
        limit: int = 100, offset: int = 0,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> List[ActionDoc]:
    user_orm = UserORM(id=UUID(user_res.user.id))
    action_find = ActionFind(id=id, name=name, version=version, type=type)
    action_docs = await UserActions(user=user_orm).list_actions(action_find, db, limit, offset)
    return action_docs


@router.get("/{id}")
async def get_action(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    action_doc = await UserActions(user=user_orm).get_action(id, db)
    return action_doc


@router.put("/{id}")
async def update_action(
        id: str,
        action_update: ActionUpdate,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    action_doc = await UserActions(user=user_orm).update_action(id, action_update, db)
    return action_doc


@router.delete("/{id}")
async def delete_action(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_actions = UserActions(user=user_orm)
    action_doc = await user_actions.get_action(id, db)
    if action_doc is None:
        raise HTTPException(400, "Action not found")
    deleted_count = await user_actions.delete_action(id, db)
    if deleted_count != 1:
        raise HTTPException(500, "Error in deleting action")
    return action_doc


@router.post("/{id}/run")
async def run_action(
        id: str,
        input: TextObj,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> Any:
    user_orm = UserORM(id=UUID(user_res.user.id))
    resp = await UserActions(user=user_orm).run_action(id, input, db)
    return resp

