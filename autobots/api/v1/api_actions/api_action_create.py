from uuid import UUID

import gotrue
from fastapi import Depends, HTTPException, APIRouter
from pymongo.database import Database

from autobots.action.action_doc_model import ActionDoc, ActionCreate
from autobots.action.action_types import ActionType
from autobots.action.user_actions import UserActions
from autobots.auth.security import get_user_from_access_token
from autobots.conn.openai.chat import ChatReq
from autobots.conn.openai.image_model import ImageReq
from autobots.core.log import log
from autobots.database.mongo_base import get_mongo_db
from autobots.user.user_orm_model import UserORM

router = APIRouter()


class ActionCreateGenTextLlmChatOpenai(ActionCreate):
    type: ActionType = ActionType.gen_text_llm_chat_openai
    input: ChatReq


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
        log.error(e)
        raise HTTPException(500)


class ActionCreateGenImageDalleOpenai(ActionCreate):
    type: ActionType = ActionType.gen_image_dalle_openai
    input: ImageReq


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
        log.error(e)
        raise HTTPException(500)
