from typing import Optional
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pymongo.database import Database

from src.autobots.action.action.action_doc_model import ActionCreate, ActionDoc
from src.autobots.action.action.user_actions import UserActions
from src.autobots.action.action_type.action_img2img.action_img2img_virtual_try_on import Img2ImgRunModelVirtualTryOn, ActionImg2ImgOotd
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.auth.security import get_user_from_access_token
from src.autobots.conn.replicate.virtual_try_on.virtual_try_on import VirtualTryOnDiffusionInParams, VirtualTryOnOutputData
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.user.user_orm_model import UserORM

router = APIRouter()


class ActionCreateImg2ImgVirtualTryOn(ActionCreate):
    type: ActionType = ActionType.img2img_virtual_try_on
    config: VirtualTryOnDiffusionInParams
    input: Optional[Img2ImgRunModelVirtualTryOn] = None
    output: Optional[VirtualTryOnOutputData] = None


@router.post("/img2img/ootd")
async def create_action_img2img_virtual_try_on(
        action_create: ActionCreateImg2ImgVirtualTryOn,
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
async def run_action_img2img_virtual_try_on(
        action_id: str,
        action_input: Img2ImgRunModelVirtualTryOn,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> VirtualTryOnOutputData:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        action = await UserActions(user=user_orm, db=db).get_action(action_id)
        image_virtual_try_on = ActionImg2ImgOotd(
            VirtualTryOnDiffusionInParams.model_validate(action.model_dump())
        )
        resp = await image_virtual_try_on.run_action(action_input)
        return resp
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500)

