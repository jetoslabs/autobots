from http.client import HTTPException
from typing import Optional
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends
from loguru import logger
from pymongo.database import Database

from src.autobots.action.action.action_doc_model import ActionDoc, ActionCreate
from src.autobots.action.action.common_action_models import TextObj
from src.autobots.action.action.user_actions import UserActions
from src.autobots.action.action_type.action_text2audio.action_text2audio_speech_openai import (
    AudioRes,
)
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.auth.security import get_user_from_access_token
from src.autobots.conn.openai.openai_audio.speech_model import SpeechReq
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.user.user_orm_model import UserORM

router = APIRouter()


class ActionCreateText2AudioSpeechOpenai(ActionCreate):
    type: ActionType = ActionType.text2audio_speech_openai
    config: SpeechReq
    input: Optional[TextObj] = None
    output: Optional[AudioRes] = None


@router.post("/text2audio/speech_openai")
async def create_action_text2audio_speech_openai(
    action_create: ActionCreateText2AudioSpeechOpenai,
    user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
    db: Database = Depends(get_mongo_db),
) -> ActionDoc:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        action_doc = await UserActions(user_orm, db).create_action(
            ActionCreate(**action_create.model_dump())
        )
        return action_doc
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500)
