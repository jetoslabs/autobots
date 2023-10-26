from typing import List, Any, Dict
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends
from pymongo.database import Database

from autobots.action.action.action_doc_model import ActionDoc, ActionFind
from autobots.action.action_type.action_types import ActionType
from autobots.action.action_market.user_actions_market import UserActionsMarket
from autobots.auth.security import get_user_from_access_token
from autobots.core.database.mongo_base import get_mongo_db
from autobots.user.user_orm_model import UserORM

router = APIRouter()


@router.post("/{id}/market/")
async def create_market_action(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_market_actions = UserActionsMarket(user_orm, db)
    updated_action = await user_market_actions.create_market_action(id)
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
    user_market_actions = UserActionsMarket(user_orm, db)
    action_find = ActionFind(
        id=id, user_id=user_id, name=name,
        version=version, type=type, is_published=True
    )
    action_docs = await user_market_actions.list_market_actions(action_find, limit, offset)
    return action_docs


@router.get("/{id}/market")
async def get_market_action(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionDoc | None:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_actions_market = UserActionsMarket(user_orm, db)
    action_doc = await user_actions_market.get_market_action(id)
    return action_doc


@router.delete("/{id}/market")
async def delete_market_action(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_actions_market = UserActionsMarket(user_orm, db)
    action_doc = await user_actions_market.delete_market_action(id)
    return action_doc


@router.post("/{id}/market/run")
async def run_market_action(
        id: str,
        input: Dict[str, Any],
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> Any:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_market_action = UserActionsMarket(user_orm, db)
    resp = await user_market_action.run_market_action(id, input)
    return resp
