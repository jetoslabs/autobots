from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pymongo.database import Database
from typing import Optional
from src.autobots.action.action.action_doc_model import ActionDoc, ActionCreate
from src.autobots.action.action.user_actions import UserActions
from src.autobots.action.action_type.action_img2img.action_img2img_bulkedit_claid import ActionImg2BulkEditClaid
from src.autobots.action.action_type.action_img2img.action_img2img_photoshoot_claid import ActionImg2ImgPhotoshootClaid
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.auth.security import get_user_from_access_token
from src.autobots.conn.claid.claid_model import ClaidRequestModel, ClaidResponse, ClaidPhotoShootRequestModel, \
    ClaidPhotoShootOutputModel
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.user.user_orm_model import UserORM

router = APIRouter()
class ActionCreateImg2ImgBulkEditClaid(ActionCreate):
    type: ActionType = ActionType.img2img_bulk_edit_claid
    config: ClaidRequestModel
    input: Optional[ClaidRequestModel] = None
    output: Optional[ClaidResponse] = None



@router.post("/img2img/bulk_edit/claid")
async def create_action_img2img_bulk_edit_claid(
        action_create: ActionCreateImg2ImgBulkEditClaid,
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


@router.post("/img2img/bulk_edit/claid/{action_id}/run")
async def run_action_img2img_bulk_edit_claid(
        action_id: str,
        action_input: ClaidRequestModel,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ClaidResponse:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        action = await UserActions(user=user_orm, db=db).get_action(action_id)
        bulk_edit_claid = ActionImg2BulkEditClaid(
            ClaidRequestModel.model_validate(action.model_dump())
        )
        resp = await bulk_edit_claid.run_action(action_input)
        return resp
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500)

@router.post("/img2img/photoshoot/claid/run")
async def run_action_img2img_photoshoot_claid(
        action_id: str,
        action_input: ClaidPhotoShootRequestModel,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ClaidPhotoShootOutputModel:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        action = await UserActions(user=user_orm, db=db).get_action(action_id)
        photoshoot_claid = ActionImg2ImgPhotoshootClaid(
            ClaidPhotoShootRequestModel.model_validate(action.model_dump())
        )
        resp = await photoshoot_claid.run_action(action_input)
        return resp
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500)
