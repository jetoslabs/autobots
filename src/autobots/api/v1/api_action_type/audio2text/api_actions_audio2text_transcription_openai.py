from typing import Optional
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase
from openai.types.audio import Transcription

from src.autobots.action.action.action_doc_model import ActionCreate, ActionDoc
from src.autobots.action.action.user_actions import UserActions
from src.autobots.action.action_type.action_audio2text.action_audio2text_transcription_openai import AudioRes
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.auth.security import get_user_from_access_token
from src.autobots.conn.openai.openai_audio.transcription_model import TranscriptionReq
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.user.user_orm_model import UserORM

router = APIRouter()


class ActionCreateAudio2TextTranscriptionOpenai(ActionCreate):
    type: ActionType = ActionType.audio2text_transcription_openai
    config: TranscriptionReq
    input: Optional[AudioRes] = None
    output: Optional[Transcription] = None


@router.post("/audio2text/transcription_openai")
async def create_action_audio2text_transcription_openai(
        action_create: ActionCreateAudio2TextTranscriptionOpenai,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
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
