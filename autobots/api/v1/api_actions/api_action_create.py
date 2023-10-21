from uuid import UUID

import gotrue
from fastapi import Depends, HTTPException, APIRouter
from pymongo.database import Database

from autobots.action.action_doc_model import ActionDoc, ActionCreate
from autobots.action.action_type.action_text2img.action_gen_image_dalle_openai_v2 import ActionCreateGenImageDalleOpenai
from autobots.action.action_type.action_text2img.action_gen_image_stability_ai_v2 import ActionCreateGenImageStabilityAi
from autobots.action.action_type.action_text2text.action_gen_text_llm_chat_openai_v2 import \
    ActionCreateGenTextLlmChatOpenai
from autobots.action.action_type.action_text2text.action_gen_text_llm_chat_with_vector_search_openai import \
    ActionCreateGenTextLlmChatWithVectorSearchOpenai
from autobots.action.user_actions import UserActions
from autobots.auth.security import get_user_from_access_token
from autobots.core.log import log
from autobots.database.mongo_base import get_mongo_db
from autobots.user.user_orm_model import UserORM

router = APIRouter()


@router.post("/gen_text/llm_chat/openai")
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
        log.exception(e)
        raise HTTPException(500)


@router.post("/gen_image/dalle/openai")
async def create_action_gen_image_dalle_openai(
        action_create: ActionCreateGenImageDalleOpenai,
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
        log.exception(e)
        raise HTTPException(500)


@router.post("/gen_image/stability_ai")
async def create_action_gen_image_stability_ai(
        action_create: ActionCreateGenImageStabilityAi,
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
        log.exception(e)
        raise HTTPException(500)


@router.post("/gen_text/llm_chat_with_vector_search_openai")
async def create_action_gen_text_llm_chat_with_vector_search_openai(
        action_create: ActionCreateGenTextLlmChatWithVectorSearchOpenai,
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
        log.exception(e)
        raise HTTPException(500)
