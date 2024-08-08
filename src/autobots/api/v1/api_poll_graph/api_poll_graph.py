
from typing import Optional
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette.requests import Request
from src.autobots.action.action.common_action_models import TextObj

from src.autobots import SettingsProvider
from src.autobots.poll_graph.poll_graph_user_actions import UserPollGraphActions
from src.autobots.poll_graph.poll_graph_user_market import UserPollGraphMarket
from src.autobots.poll_graph.poll_graph_result import PollGraphResultDoc, UserPollGraphResult
from src.autobots.api.webhook import Webhook
from src.autobots.auth.security import get_user_from_access_token
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.poll_graph.poll_graph_doc_model import PollGraphDoc, PollGraphCreate, \
    PollGraphFind, PollGraphUpdate, PollGraphDocsFound, PollGraphPublishedDocFind
from src.autobots.poll_graph.user_poll_graph import UserPollGraph

from src.autobots.user.user_orm_model import UserORM

router = APIRouter(prefix=SettingsProvider.sget().API_POLL_GRAPHS, tags=[SettingsProvider.sget().API_POLL_GRAPHS])


@router.post("/")
async def create_poll_graph(
        poll_graph_create: PollGraphCreate,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> PollGraphDoc:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        resp = await UserPollGraph(user=user_orm, db=db).create(poll_graph_create)
        return resp
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500)


@router.get("/")
async def list_poll_graphs(
        id: str = None, name: str = None, version: float = None, is_published: bool = None,
        is_published_by_others: bool = True,
        limit: int = 100, offset: int = 0,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> PollGraphDocsFound:
    user_orm = UserORM(id=UUID(user_res.user.id))
    find = PollGraphFind(id=id, name=name, version=version, is_published=is_published)
    or_find = None
    if is_published_by_others:
        or_find = [PollGraphPublishedDocFind()]
    poll_graph_docs = await UserPollGraph(user=user_orm, db=db).list_owned_or_published(find, or_find, limit, offset)
    return poll_graph_docs


@router.get("/{id}")
async def get_poll_graph(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> PollGraphDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    poll_graph_doc = await UserPollGraph(user=user_orm, db=db).get_owned_or_published(id)
    if not poll_graph_doc:
        raise HTTPException(404, detail="Poll graph not found")
    return poll_graph_doc


@router.put("/{id}")
async def update_poll_graph(
        id: str,
        poll_graph_update: PollGraphUpdate,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> PollGraphDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    poll_graph_doc = await UserPollGraph(user=user_orm, db=db).update(id, poll_graph_update)
    return poll_graph_doc


@router.delete("/{id}")
async def delete_poll_graph(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> PollGraphDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_poll_graphs = UserPollGraph(user=user_orm, db=db)
    poll_graph_doc = await user_poll_graphs.get_owned(id)
    if poll_graph_doc is None:
        raise HTTPException(404, "Poll graph not found")
    deleted_count = await user_poll_graphs.delete(id)
    if deleted_count != 1:
        raise HTTPException(500, "Error in deleting poll graph")
    return poll_graph_doc


# @router.post("/{id}/run")
# async def run_poll_graph(
#         id: str,
#         input: TextObj,
#         user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
#         db: Database = Depends(get_mongo_db)
# ) -> Dict[str, Any]:
#     user_orm = UserORM(id=UUID(user_res.user.id))
#     resp = await UserPollGraph(user=user_orm, db=db).run(id, input, db)
#     return resp


@router.post("/{id}/async_run")
async def async_run_poll_graph(
        request: Request,
        id: str,
        input: TextObj,
        background_tasks: BackgroundTasks,
        poll_graph_result_id: Optional[str] = None,
        poll_graph_node_id: Optional[str] = None,
        webhook: Webhook | None = None,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> PollGraphResultDoc | None:
    ctx = request.state.context
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_poll_graph_actions = UserPollGraphActions(user_orm, db)
    user_poll_graph_market = UserPollGraphMarket(user_orm, db)
    user_poll_graph_result = UserPollGraphResult(user_orm, db)
    resp = await UserPollGraph(user=user_orm, db=db).run_in_background(
        ctx,
        user_poll_graph_actions,
        user_poll_graph_market,
        user_poll_graph_result,
        id,
        input,
        poll_graph_result_id,
        poll_graph_node_id,
        background_tasks,
        webhook
    )
    return resp


