from typing import List, Any, Dict
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from autobots.action.action_doc_model import ActionUpdate, ActionDoc, ActionFind
from autobots.action.action_type.action_types import ActionType
from autobots.action.user_actions import UserActions
from autobots.auth.security import get_user_from_access_token
from autobots.database.mongo_base import get_mongo_db
from autobots.user.user_orm_model import UserORM

router = APIRouter()


@router.post("/{id}/market/")
async def create_market_action(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_actions = UserActions(user_orm)
    action_doc = await user_actions.get_action(id, db)
    # Check if action being published is owned by user
    if not action_doc or not user_res.user.id == action_doc.user_id:
        raise HTTPException(403, "User dont own this action")
    # publish action
    action_update = ActionUpdate(is_published=True)
    updated_action = await user_actions.update_action(id, action_update, db)
    return updated_action


@router.get("/market")
async def list_market_actions(
        id: str = None, user_id: str = None, name: str = None,
        version: float = None, type: ActionType = None,
        limit: int = 100, offset: int = 0,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> List[ActionDoc]:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_actions = UserActions(user_orm)
    action_find = ActionFind(
        id=id, user_id=user_id, name=name,
        version=version, type=type, is_published=True
    )
    action_docs = await user_actions.list_market_actions(action_find, db, limit, offset)
    return action_docs


@router.get("/{id}/market")
async def get_market_action(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_actions = UserActions(user_orm)
    action_find = ActionFind(
        id=id, is_published=True
    )
    action_docs = await user_actions.list_market_actions(action_find, db, 1, 0)
    return action_docs[0]


@router.delete("/{id}/market")
async def delete_market_action(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_actions = UserActions(user_orm)
    action_doc = await user_actions.get_action(id, db)
    # Check if action being published is owned by user
    if not action_doc or not user_res.user.id == action_doc.user_id:
        raise HTTPException(403, "User dont own this action")
    # publish action
    action_update = ActionUpdate(is_published=False)
    updated_action = await user_actions.update_action(id, action_update, db)
    return updated_action


@router.post("/{id}/market/run")
async def run_market_action(
        id: str,
        input: Dict[str, Any],
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> Any:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_actions = UserActions(user_orm)
    action_find = ActionFind(
        id=id, is_published=True
    )
    action_docs = await user_actions.list_actions(action_find, db, 1, 0)
    action_doc = action_docs[0]
    resp = await user_actions.test_action(action_doc, input)
    return resp
