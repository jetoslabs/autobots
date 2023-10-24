from typing import List
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from autobots.action.common_action_models import TextObj
from autobots.action.user_actions import UserActions
from autobots.auth.security import get_user_from_access_token
from autobots.chat.chat_doc_model import ChatDoc, ChatFind, ChatUpdate, ChatCreate
from autobots.chat.user_chat import UserChat
from autobots.database.mongo_base import get_mongo_db

from autobots.user.user_orm_model import UserORM

router = APIRouter()


@router.post("/")
async def create_chat(
        action_id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ChatDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    action_doc = await UserActions(user=user_orm).get_action(action_id, db)
    chat_create = ChatCreate(action=action_doc, messages=[])
    chat_doc = await UserChat(user=user_orm, db=db).create_chat(chat_create)
    return chat_doc


@router.get("/")
async def list_chat(
        id: str = None, title: str = None,
        limit: int = 100, offset: int = 0,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> List[ChatDoc]:
    user_orm = UserORM(id=UUID(user_res.user.id))
    chat_find = ChatFind(id=id, title=title)
    chat_docs = await UserChat(user=user_orm, db=db).list_chat(chat_find, limit, offset)
    return chat_docs


@router.get("/{id}")
async def get_chat(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ChatDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    chat_doc = await UserChat(user=user_orm, db=db).get_chat(id)
    return chat_doc


@router.put("/{id}")
async def update_chat(
        id: str,
        chat_update: ChatUpdate,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ChatDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    chat_doc = await UserChat(user=user_orm, db=db).update_chat(id, chat_update)
    return chat_doc


@router.delete("/{id}")
async def delete_chat(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ChatDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_chat = UserChat(user=user_orm, db=db)
    chat_doc = await user_chat.get_chat(id)
    if chat_doc is None:
        raise HTTPException(400, "Action not found")
    deleted_count = await user_chat.delete_chat(id)
    if deleted_count != 1:
        raise HTTPException(500, "Error in deleting action")
    return chat_doc


@router.post("/{id}")
async def chat(
        id: str,
        input: TextObj,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> str:
    user_orm = UserORM(id=UUID(user_res.user.id))
    resp = await UserChat(user=user_orm, db=db).chat(id, input)
    return resp.messages[-1].content
