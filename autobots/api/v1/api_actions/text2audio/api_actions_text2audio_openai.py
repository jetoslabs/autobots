from http.client import HTTPException
from typing import Optional
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends
from pymongo.database import Database

from autobots.action.action.action_doc_model import ActionDoc, ActionCreate
from autobots.action.action.common_action_models import TextObj
from autobots.action.action.user_actions import UserActions
from autobots.action.action_type.action_text2audio.action_text2audio_openai import AudioRes
from autobots.action.action_type.action_types import ActionType
from autobots.auth.security import get_user_from_access_token
from autobots.conn.openai.speech_model import SpeechReq
from autobots.core.database.mongo_base import get_mongo_db
from autobots.core.log import log
from autobots.user.user_orm_model import UserORM

router = APIRouter()


class ActionCreateText2AudioOpenai(ActionCreate):
    type: ActionType = ActionType.text2audio_openai
    config: SpeechReq
    input: Optional[TextObj] = None
    output: Optional[AudioRes] = None


@router.post("/text2audio/openai")
async def create_action_text2audio_openai(
        action_create: ActionCreateText2AudioOpenai,
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
        log.exception(e)
        raise HTTPException(500)
