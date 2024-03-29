from typing import List, Optional
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from loguru import logger
from pymongo.database import Database

from src.autobots import SettingsProvider
from src.autobots.action.action.common_action_models import TextObj
from src.autobots.action.action.user_actions import UserActions
from src.autobots.action.action_market.user_actions_market import UserActionsMarket
from src.autobots.action_graph.action_graph_result.action_graph_result_model_doc import ActionGraphResultDoc
from src.autobots.action_graph.action_graph_result.user_action_graph_result import UserActionGraphResult
from src.autobots.api.webhook import Webhook
from src.autobots.auth.security import get_user_from_access_token
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.action_graph.action_graph.action_graph_doc_model import ActionGraphDoc, ActionGraphCreate, ActionGraphFind, ActionGraphUpdate
from src.autobots.action_graph.action_graph.user_action_graph import UserActionGraphs

from src.autobots.user.user_orm_model import UserORM

router = APIRouter(prefix=SettingsProvider.sget().API_ACTION_GRAPHS, tags=[SettingsProvider.sget().API_ACTION_GRAPHS])


@router.post("/")
async def create_action_graph(
        action_graph_create: ActionGraphCreate,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionGraphDoc:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        resp = await UserActionGraphs(user=user_orm, db=db).create(action_graph_create, db)
        return resp
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500)


@router.get("/")
async def list_action_graphs(
        id: str = None, name: str = None, version: float = None,
        limit: int = 100, offset: int = 0,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> List[ActionGraphDoc]:
    user_orm = UserORM(id=UUID(user_res.user.id))
    find = ActionGraphFind(id=id, name=name, version=version)
    action_docs = await UserActionGraphs(user=user_orm, db=db).list(find, db, limit, offset)
    return action_docs


@router.get("/{id}")
async def get_action_graph(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionGraphDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    action_doc = await UserActionGraphs(user=user_orm, db=db).get(id, db)
    return action_doc


@router.put("/{id}")
async def update_action_graph(
        id: str,
        action_graph_update: ActionGraphUpdate,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionGraphDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    action_doc = await UserActionGraphs(user=user_orm, db=db).update(id, action_graph_update, db)
    return action_doc


@router.delete("/{id}")
async def delete_action_graph(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionGraphDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_action_graphs = UserActionGraphs(user=user_orm, db=db)
    action_doc = await user_action_graphs.get(id, db)
    if action_doc is None:
        raise HTTPException(400, "Action not found")
    deleted_count = await user_action_graphs.delete(id, db)
    if deleted_count != 1:
        raise HTTPException(500, "Error in deleting action")
    return action_doc


# @router.post("/{id}/run")
# async def run_action_graph(
#         id: str,
#         input: TextObj,
#         user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
#         db: Database = Depends(get_mongo_db)
# ) -> Dict[str, Any]:
#     user_orm = UserORM(id=UUID(user_res.user.id))
#     resp = await UserActionGraphs(user=user_orm, db=db).run(id, input, db)
#     return resp


@router.post("/{id}/async_run")
async def async_run_action_graph(
        id: str,
        input: TextObj,
        background_tasks: BackgroundTasks,
        action_graph_result_id: Optional[str] = None,
        webhook: Webhook | None = None,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionGraphResultDoc | None:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_actions = UserActions(user_orm, db)
    user_actions_market = UserActionsMarket(user_orm, db)
    user_action_graph_result = UserActionGraphResult(user_orm, db)
    resp = await UserActionGraphs(user=user_orm, db=db).run_in_background(
        user_actions,
        user_actions_market,
        user_action_graph_result,
        id,
        input,
        action_graph_result_id,
        background_tasks,
        webhook
    )
    return resp
