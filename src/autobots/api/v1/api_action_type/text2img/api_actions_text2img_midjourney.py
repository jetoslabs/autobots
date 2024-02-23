from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from autobots.action.action.action_doc_model import ActionDoc, ActionCreate
from autobots.action.action_type.action_text2img.action_text2img_midjourney import ActionText2ImgMidjourney, \
    ActionCreateText2ImgMidJourney
from autobots.action.action.user_actions import UserActions
from autobots.api.v1.api_action_type.text2img.api_actions_text2img_midjourney_model import ActionCreateAPIModelText2ImgMidjourney
from autobots.auth.security import get_user_from_access_token
from autobots.conn.useapi.text2img.text2img_model import DiscordJobReqModel, DiscordImagineApiResponse, \
    DiscordErrorResponse
from autobots.core.database.mongo_base import get_mongo_db
from autobots.core.logging.log import Log
from autobots.user.user_orm_model import UserORM

router = APIRouter()


@router.post("/text2img/mid_journey")
async def create_action_text2img_midjourney(
        action: ActionCreateAPIModelText2ImgMidjourney,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionDoc:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        action_create = ActionCreateText2ImgMidJourney(**action.model_dump())
        action_doc = await UserActions(user_orm, db).create_action(
            ActionCreate(**action_create.model_dump())
        )
        return action_doc
    except Exception as e:
        Log.error(str(e))
        raise HTTPException(500)


@router.post("/text2img/mid_journey/{action_id}/run")
async def run_action_text2img_stable_diffusion(
        action_id: str,
        action_input: DiscordJobReqModel,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> DiscordImagineApiResponse | DiscordErrorResponse:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        action = await UserActions(user=user_orm, db=db).get_action(action_id)
        text2img = ActionText2ImgMidjourney(
            DiscordJobReqModel.model_validate(action.config)
        )
        resp = await text2img.run_action(action_input)
        return resp
    except Exception as e:
        Log.error(str(e))
        raise HTTPException(500)
