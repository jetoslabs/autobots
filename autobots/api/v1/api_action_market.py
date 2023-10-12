from typing import List, Any
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from autobots.action.action_type.action_types import ActionType
from autobots.action.user_actions import UserActions
from autobots.action_market.action_market_doc_model import ActionMarketDoc, ActionMarketCreate, ActionMarketUpdate, \
    ActionMarketFind
from autobots.action_market.user_action_market import UserActionMarket
from autobots.auth.security import get_user_from_access_token
from autobots.database.mongo_base import get_mongo_db
from autobots.prompts.user_prompts import TextObj
from autobots.user.user_orm_model import UserORM

router = APIRouter()


@router.post("/")
async def create_market_action(
        id: str,
        # market_action_create: ActionMarketCreate,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionMarketDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    action_doc = await UserActions(user_orm).get_action(id, db)
    # Check if action being published is owned by user
    if not action_doc or not user_res.user.id == action_doc.user_id:
        raise HTTPException(403, "User dont own this action")
    # create market action
    market_action_create = ActionMarketCreate(action=action_doc)
    market_action_doc = await UserActionMarket(user_orm, db).create_market_action(market_action_create)
    return market_action_doc


@router.get("/")
async def list_market_actions(
        id: str = None, action_user_id: str = None, action_name: str = None,
        action_version: float = None, action_type: ActionType = None,
        limit: int = 100, offset: int = 0,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> List[ActionMarketDoc]:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_action_market = UserActionMarket(user_orm, db)
    action_market_find = ActionMarketFind(
        id=id, action_user_id=action_user_id, action_name=action_name,
        action_version=action_version, action_type=action_type
    )
    action_market_docs = await user_action_market.list_market_actions(action_market_find, limit, offset)
    return action_market_docs


@router.get("/{id}")
async def get_market_action(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionMarketDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    action_market_doc = await UserActionMarket(user_orm, db).get_market_action(id)
    return action_market_doc


@router.put("/{id}")
async def update_market_action(
        id: str,
        # market_action_update: ActionMarketUpdate,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionMarketDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_action_market = UserActionMarket(user_orm, db)
    # get action in market action
    action_market_doc = await user_action_market.get_market_action(id)
    action_id = action_market_doc.action.id
    action_doc = await UserActions(user_orm).get_action(action_id, db)
    # Check if action being updated is owned by user
    if not action_doc or not user_res.user.id == action_doc.user_id:
        raise HTTPException(403, "User dont own this action")
    # update market action
    market_action_update = ActionMarketUpdate(action=action_doc)
    action_market_doc = await UserActionMarket(user_orm, db).update_market_action(id, market_action_update)
    return action_market_doc


@router.delete("/{id}")
async def delete_market_action(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionMarketDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_action_market = UserActionMarket(user_orm, db)
    market_action = await user_action_market.get_market_action(id)
    if not market_action:
        raise HTTPException(404, "Market Action not found")
    deleted = await UserActionMarket(user_orm, db).delete_market_action(id)
    if deleted != 1:
        raise HTTPException(500, "Error in deleting market action")
    return market_action


@router.post("/{id}/run")
async def run_market_action(
        id: str,
        input: TextObj,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> Any:
    user_orm = UserORM(id=UUID(user_res.user.id))
    resp = await UserActionMarket(user=user_orm, db=db).run_market_action(id, input)
    return resp
