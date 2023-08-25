from typing import List
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from autobots.action.action_doc_model import ActionCreate, ActionDoc, ActionFind, ActionCreateGenTextLlmChatOpenai, \
    ActionUpdate
from autobots.action.action_manager import ActionManager
from autobots.action.action_types import ActionType
from autobots.action.user_actions import UserActions
from autobots.auth.security import get_user_from_access_token
from autobots.conn.openai.chat import Message, Role
from autobots.core.log import log
from autobots.database.mongo_base import get_mongo_db
from autobots.prompts.user_prompts import Input
from autobots.user.user_orm_model import UserORM

router = APIRouter()


@router.get("/types")
async def get_action_types(
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token)
) -> List[str]:
    return ActionManager.get_action_types()


@router.post("/gen_text_llm_chat_openai")
async def create_action_gen_text_llm_chat_openai(
        action_create: ActionCreateGenTextLlmChatOpenai,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionDoc:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        action_doc = await UserActions(user_orm).create_action(
            ActionCreate(**action_create.model_dump()), db
        )
        return action_doc
    except Exception as e:
        log.error(e)
        raise HTTPException(500)


@router.get("/list")
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
async def delete_prompt(
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
        input: Input,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> Message:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_actions = UserActions(user=user_orm)
    user_message = Message(role=Role.user, content=input.input)
    resp_message = await user_actions.run_action(id, user_message, db)
    return resp_message

