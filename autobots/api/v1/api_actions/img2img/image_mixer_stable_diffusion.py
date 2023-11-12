from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from pymongo.database import Database

from autobots.action.action.action_doc_model import ActionDoc, ActionCreate
from autobots.action.action_type.action_img2img.action_image_mixer_stable_diffusion import \
    ActionCreateImageMixerStableDiffusion, ActionImageMixerStableDiffusion, ImageMixerRunModel
from autobots.action.action.user_actions import UserActions
from autobots.auth.security import get_user_from_access_token
from autobots.conn.stable_diffusion.common_models import StableDiffusionRes
from autobots.conn.stable_diffusion.image_mixer.image_mixer_model import ImageMixerReqModel
from autobots.core.log import log
from autobots.core.database.mongo_base import get_mongo_db
from autobots.user.user_orm_model import UserORM

router = APIRouter()


@router.post("/img2img/image_mixer_stable_diffusion")
async def create_action_image_mixer_stable_diffusion(
        action_create: ActionCreateImageMixerStableDiffusion,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ActionDoc:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        action_doc = await UserActions(user_orm).create_action(
            ActionCreate(**action_create.model_dump()), db
        )
        return action_doc
    except Exception as e:
        log.exception(e)
        raise HTTPException(500)


@router.post("/img2img/image_mixer/stable_diffusion/{action_id}/run")
async def run_action_image_mixer_stable_diffusion(
        action_id: str,
        action_input: ImageMixerRunModel,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> StableDiffusionRes:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        action = await UserActions(user=user_orm).get_action(action_id, db)
        image_mixer = ActionImageMixerStableDiffusion(
            ImageMixerReqModel.model_validate(action.model_dump())
        )
        resp = await image_mixer.run_action(action_input)
        return resp
    except Exception as e:
        log.exception(e)
        raise HTTPException(500)

