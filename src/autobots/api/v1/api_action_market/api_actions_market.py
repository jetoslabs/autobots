from typing import List, Any, Dict
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette.requests import Request

from src.autobots import SettingsProvider
from src.autobots.action.action.action_doc_model import ActionDoc
from src.autobots.action.action_market.action_market_model import ActionMarketFind
from src.autobots.action.action_result.action_result_doc_model import ActionResultDoc
from src.autobots.action.action_result.user_action_result import UserActionResult
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.action.action_market.user_actions_market import UserActionsMarket
from src.autobots.api.webhook import Webhook
from src.autobots.auth.security import get_user_from_access_token
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.user.user_orm_model import UserORM

router = APIRouter(prefix=SettingsProvider.sget().API_ACTIONS_MARKET, tags=[SettingsProvider.sget().API_ACTIONS_MARKET])


@router.post("/{id}/market/")
async def create_market_action(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
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
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> List[ActionDoc]:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_market_actions = UserActionsMarket(user_orm, db)
    action_market_find = ActionMarketFind(
        id=id, name=name,
        version=version, type=type, is_published=True
    )
    action_docs = await user_market_actions.list_market_actions(action_market_find, limit, offset)
    return action_docs


@router.get("/{id}/market")
async def get_market_action(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> ActionDoc | None:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_actions_market = UserActionsMarket(user_orm, db)
    action_doc = await user_actions_market.get_market_action(id)
    return action_doc


@router.delete("/{id}/market")
async def delete_market_action(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> ActionDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_actions_market = UserActionsMarket(user_orm, db)
    action_doc = await user_actions_market.delete_market_action(id)
    return action_doc


@router.post("/{id}/market/run")
async def run_market_action(
        request: Request,
        id: str,
        input: Dict[str, Any],
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> ActionDoc:
    ctx = request.state.context
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_market_action = UserActionsMarket(user_orm, db)
    resp = await user_market_action.run_market_action(ctx, id, input)
    return resp


@router.post("/{id}/market/async_run")
async def async_run_action(
        request: Request,
        id: str,
        input: Dict[str, Any],
        background_tasks: BackgroundTasks,
        webhook: Webhook | None = None,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db),
) -> ActionResultDoc:
    ctx = request.state.context
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_market_action = UserActionsMarket(user_orm, db)
    user_action_result = UserActionResult(user_orm, db)
    resp = await user_market_action.run_market_action_async(
        ctx=ctx, action_id=id, input=input, user_action_result=user_action_result,
        background_tasks=background_tasks, webhook=webhook
    )
    return resp
