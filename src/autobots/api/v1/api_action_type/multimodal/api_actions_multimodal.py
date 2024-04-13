from typing import Optional
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pymongo.database import Database

from src.autobots.action.action.action_doc_model import ActionDoc, ActionCreate
from src.autobots.action.action.common_action_models import TextObj, TextObjs
from src.autobots.action.action.user_actions import UserActions
from src.autobots.action.action_type.action_multimodal.action_multimodal_assistant_openai.assistant_openai_model import \
    AssistantOpenaiConfigCreate
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.auth.security import get_user_from_access_token
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.user.user_orm_model import UserORM

router = APIRouter()


class ActionCreateMultimodalAssistantOpenai(ActionCreate):
    type: ActionType = ActionType.multimodal_assistant_openai
    config: AssistantOpenaiConfigCreate
    input: Optional[TextObj] = None
    output: Optional[TextObjs] = None


@router.post("/multimodal/assistant_openai")
async def create_action_multimodal_assistant_openai(
        action_create: ActionCreateMultimodalAssistantOpenai,
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
        logger.exception(str(e))
        raise HTTPException(500, detail=str(e))
