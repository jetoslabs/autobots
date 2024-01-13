from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from autobots.action.action.action_doc_model import ActionDoc, ActionCreate
from autobots.action.action.user_actions import UserActions
from autobots.action.action_type.action_text2text.action_text2text_llm_chat_openai_v2 import \
    ActionCreateText2TextLlmChatOpenai
from autobots.action.action_type.action_text2text.action_text2text_llm_chat_with_vector_search_openai import \
    ActionCreateText2TextLlmChatWithVectorSearchOpenai
from autobots.action.action_type.action_text2text.action_text2text_read_url import ReadUrlConfig
from autobots.action.action_type.action_text2text.action_text2text_search_map import SearchMapsConfig
from autobots.action.action_type.action_text2text.action_text2text_search_web import SearchWebConfig
from autobots.action.action_type.action_types import ActionType
from autobots.auth.security import get_user_from_access_token
from autobots.core.database.mongo_base import get_mongo_db
from autobots.core.logging.log import Log
from autobots.user.user_orm_model import UserORM

router = APIRouter()


@router.post("/text2text/llm_chat_openai")
async def create_action_text2text_llm_chat_openai(
        action_create: ActionCreateText2TextLlmChatOpenai,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionDoc:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        action_doc = await UserActions(user_orm, db).create_action(
            ActionCreate(**action_create.model_dump())
        )
        return action_doc
    except Exception as e:
        Log.error(str(e))
        raise HTTPException(500)


@router.post("/text2text/llm_chat_with_vector_search_openai")
async def create_action_text2text_llm_chat_with_vector_search_openai(
        action_create: ActionCreateText2TextLlmChatWithVectorSearchOpenai,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionDoc:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        action_doc = await UserActions(user_orm, db).create_action(
            ActionCreate(**action_create.model_dump())
        )
        return action_doc
    except Exception as e:
        Log.error(str(e))
        raise HTTPException(500)


class ActionCreateText2TextReadUrl(ActionCreate):
    type: ActionType = ActionType.text2text_read_url
    config: ReadUrlConfig


@router.post("/text2text/read_url")
async def create_action_text2text_read_url(
        action_create: ActionCreateText2TextReadUrl,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionDoc:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        action_doc = await UserActions(user_orm, db).create_action(
            ActionCreate(**action_create.model_dump())
        )
        return action_doc
    except Exception as e:
        Log.error(str(e))
        raise HTTPException(500)


class ActionCreateText2TextSearchWeb(ActionCreate):
    type: ActionType = ActionType.text2text_search_web
    config: SearchWebConfig


@router.post("/text2text/search_web")
async def create_action_text2text_search_web(
        action_create: ActionCreateText2TextSearchWeb,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionDoc:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        action_doc = await UserActions(user_orm, db).create_action(
            ActionCreate(**action_create.model_dump(exclude_none=True))
        )
        return action_doc
    except HTTPException as e:
        raise
    except Exception as e:
        Log.error(str(e))
        raise HTTPException(500)


class ActionCreateText2TextSearchMaps(ActionCreate):
    type: ActionType = ActionType.text2text_search_maps
    config: SearchMapsConfig


@router.post("/text2text/search_maps")
async def create_action_text2text_search_maps(
        action_create: ActionCreateText2TextSearchMaps,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionDoc:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        action_doc = await UserActions(user_orm, db).create_action(
            ActionCreate(**action_create.model_dump(exclude_none=True))
        )
        return action_doc
    except HTTPException as e:
        raise
    except Exception as e:
        Log.error(str(e))
        raise HTTPException(500)
