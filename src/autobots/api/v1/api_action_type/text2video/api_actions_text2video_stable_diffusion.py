from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.autobots.action.action.action_doc_model import ActionDoc, ActionCreate
from src.autobots.action.action_type.action_text2video.action_text2video_stable_diffusion import \
    ActionCreateText2VideoStableDiffusion, ActionText2VideoStableDiffusion, Text2VideoRunModel
from src.autobots.action.action.user_actions import UserActions
from src.autobots.api.v1.api_action_type.text2video.api_actions_text2video_stable_diffusion_model import \
    ActionCreateAPIModelText2VideoStableDiffusion
from src.autobots.auth.security import get_user_from_access_token
from src.autobots.conn.stable_diffusion.common_models import StableDiffusionRes
from src.autobots.conn.stable_diffusion.text2video.text2video_model import Text2VideoReqModel
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.user.user_orm_model import UserORM

router = APIRouter()


@router.post("/text2video/stable_diffusion")
async def create_action_text2video_stable_diffusion(
        action: ActionCreateAPIModelText2VideoStableDiffusion,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> ActionDoc:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        action_create = ActionCreateText2VideoStableDiffusion(**action.model_dump())
        action_doc = await UserActions(user_orm, db).create_action(
            ActionCreate(**action_create.model_dump())
        )
        return action_doc
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500)


@router.post("/text2video/stable_diffusion/{action_id}/run")
async def run_action_text2video_stable_diffusion(
        action_id: str,
        action_input: Text2VideoRunModel,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> StableDiffusionRes:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        action = await UserActions(user=user_orm, db=db).get_action(action_id)
        text2video = ActionText2VideoStableDiffusion(
            action_config=Text2VideoReqModel.model_validate(action.model_dump())
        )
        resp = await text2video.run_action(action_input)
        return resp
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500)
