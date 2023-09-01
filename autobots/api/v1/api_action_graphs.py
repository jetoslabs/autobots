from typing import List, Any, Dict
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from autobots.auth.security import get_user_from_access_token
from autobots.core.log import log
from autobots.database.mongo_base import get_mongo_db
from autobots.graphs.action_graph_doc_model import ActionGraphDoc, ActionGraphCreate, ActionGraphFind, ActionGraphUpdate
from autobots.graphs.user_action_graph import UserActionGraphs
from autobots.prompts.user_prompts import Input
from autobots.user.user_orm_model import UserORM

router = APIRouter()


@router.post("/")
async def create_action_graph(
        action_graph_create: ActionGraphCreate,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionGraphDoc:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        resp = await UserActionGraphs(user=user_orm).create(action_graph_create, db)
        return resp
    except Exception as e:
        log.error(e)
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
    action_docs = await UserActionGraphs(user=user_orm).list(find, db, limit, offset)
    return action_docs


@router.get("/{id}")
async def get_action_graph(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionGraphDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    action_doc = await UserActionGraphs(user=user_orm).get(id, db)
    return action_doc


@router.put("/{id}")
async def update_action_graph(
        id: str,
        action_graph_update: ActionGraphUpdate,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionGraphDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    action_doc = await UserActionGraphs(user=user_orm).update(id, action_graph_update, db)
    return action_doc


@router.delete("/{id}")
async def delete_action_graph(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionGraphDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_action_graphs = UserActionGraphs(user=user_orm)
    action_doc = await user_action_graphs.get(id, db)
    if action_doc is None:
        raise HTTPException(400, "Action not found")
    deleted_count = await user_action_graphs.delete(id, db)
    if deleted_count != 1:
        raise HTTPException(500, "Error in deleting action")
    return action_doc


@router.post("/{id}/run")
async def run_action_graph(
        id: str,
        input: Input,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> Dict[str, Any]:
    user_orm = UserORM(id=UUID(user_res.user.id))
    resp = await UserActionGraphs(user=user_orm).run(id, input, db)
    return resp

