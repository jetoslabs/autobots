from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from autobots.action.action.action_doc_model import ActionDoc, ActionCreate
from autobots.action.action.user_actions import UserActions
from autobots.action.action_type.action_text2text.action_text2text_llm_chat_openai_v2 import \
    ActionCreateGenTextLlmChatOpenai
from autobots.action.action_type.action_text2text.action_text2text_llm_chat_with_vector_search_openai import \
    ActionCreateGenTextLlmChatWithVectorSearchOpenai
from autobots.auth.security import get_user_from_access_token
from autobots.core.database.mongo_base import get_mongo_db
from autobots.core.logging.log import Log
from autobots.user.user_orm_model import UserORM

router = APIRouter()


@router.post("/text2text/llm_chat_openai")
async def create_action_gen_text_llm_chat_openai(
        action_create: ActionCreateGenTextLlmChatOpenai,
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
        Log.exception(str(e))
        raise HTTPException(500)


@router.post("/text2text/llm_chat_with_vector_search_openai")
async def create_action_gen_text_llm_chat_with_vector_search_openai(
        action_create: ActionCreateGenTextLlmChatWithVectorSearchOpenai,
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
        Log.exception(str(e))
        raise HTTPException(500)
