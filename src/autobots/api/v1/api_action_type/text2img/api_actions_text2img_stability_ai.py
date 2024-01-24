# from uuid import UUID

# import gotrue
from fastapi import APIRouter# Depends, HTTPException
# from pymongo.database import Database

# from autobots.action.action.action_doc_model import ActionDoc, ActionCreate
# from autobots.action.action.user_actions import UserActions
# from autobots.action.action_type.action_text2img.action_text2img_stability_ai_v2 import ActionCreateGenImageStabilityAi
# from autobots.auth.security import get_user_from_access_token
# from autobots.core.database.mongo_base import get_mongo_db
# from autobots.core.log import log
# from autobots.user.user_orm_model import UserORM

router = APIRouter()

# @router.post("/text2img/stability_ai")
# async def create_action_gen_image_stability_ai(
#         action_create: ActionCreateGenImageStabilityAi,
#         user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
#         db: Database = Depends(get_mongo_db)
# ) -> ActionDoc:
#     try:
#         user_orm = UserORM(id=UUID(user_res.user.id))
#         action_doc = await UserActions(user_orm, db).create_action(
#             ActionCreate(**action_create.model_dump())
#         )
#         return action_doc
#     except Exception as e:
#         log.exception(str(e))
#         raise HTTPException(500)
