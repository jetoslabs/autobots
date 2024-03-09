from typing import Optional
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pymongo.database import Database

from src.autobots.action.action.action_doc_model import ActionCreate, ActionDoc
from src.autobots.action.action.user_actions import UserActions
from src.autobots.action.action_type.action_img2img.action_img2img_ootd import Img2ImgRunModelOotd, ActionImg2ImgOotd
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.auth.security import get_user_from_access_token
from src.autobots.conn.replicate.oot_diffusion.oot_diffusion import OotdDiffusionInParams, OotdDiffusionOutputData
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.user.user_orm_model import UserORM

router = APIRouter()


class ActionCreateImg2ImgOotd(ActionCreate):
    type: ActionType = ActionType.img2img_ootd
    config: OotdDiffusionInParams
    input: Optional[Img2ImgRunModelOotd] = None
    output: Optional[OotdDiffusionOutputData] = None


@router.post("/img2img/ootd")
async def create_action_img2img_stable_diffusion(
        action_create: ActionCreateImg2ImgOotd,
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
        logger.error(str(e))
        raise HTTPException(500)


@router.post("/img2img/ootd/{action_id}/run")
async def run_action_image_mixer_stable_diffusion(
        action_id: str,
        action_input: Img2ImgRunModelOotd,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> OotdDiffusionOutputData:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        action = await UserActions(user=user_orm, db=db).get_action(action_id)
        image_ootd = ActionImg2ImgOotd(
            OotdDiffusionInParams.model_validate(action.model_dump())
        )
        resp = await image_ootd.run_action(action_input)
        return resp
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500)

