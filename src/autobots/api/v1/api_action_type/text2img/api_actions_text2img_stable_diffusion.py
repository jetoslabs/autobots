from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.autobots.action.action.action_doc_model import ActionDoc, ActionCreate
from src.autobots.action.action_type.action_text2img.action_text2img_stable_diffusion import ActionText2ImgStableDiffusion, \
    ActionCreateText2ImgStableDiffusion, Text2ImgRunModel
from src.autobots.action.action.user_actions import UserActions
from src.autobots.api.v1.api_action_type.text2img.api_actions_text2img_stable_diffusion_model import ActionCreateAPIModelText2ImgStableDiffusion
from src.autobots.auth.security import get_user_from_access_token
from src.autobots.conn.stable_diffusion.common_models import StableDiffusionRes
from src.autobots.conn.stable_diffusion.text2img.text2img_model import Text2ImgReqModel
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.user.user_orm_model import UserORM

router = APIRouter()


@router.post("/text2img/stable_diffusion")
async def create_action_text2img_stable_diffusion(
        action: ActionCreateAPIModelText2ImgStableDiffusion,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> ActionDoc:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        action_create = ActionCreateText2ImgStableDiffusion(**action.model_dump())
        action_doc = await UserActions(user_orm, db).create_action(
            ActionCreate(**action_create.model_dump())
        )
        return action_doc
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500)


@router.post("/text2img/stable_diffusion/{action_id}/run")
async def run_action_text2img_stable_diffusion(
        action_id: str,
        action_input: Text2ImgRunModel,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> StableDiffusionRes:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        action = await UserActions(user=user_orm, db=db).get_action(action_id)
        text2img = ActionText2ImgStableDiffusion(
            Text2ImgReqModel.model_validate(action.config)
        )
        resp = await text2img.run_action(action_input)
        return resp
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500)
