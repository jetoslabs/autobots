from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from autobots.auth.security import get_user_from_access_token
from autobots.database.base import get_db
from autobots.database.database_models import UserORM
from autobots.user.user_prompts import UserPrompts, UserPromptCreateInput, UserPromptCreateOutput

router = APIRouter()


@router.post("/")
async def create_prompt(
        user_prompt_create_input: UserPromptCreateInput,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Session = Depends(get_db)
) -> UserPromptCreateOutput:
    user_orm = UserORM(id=UUID(user_res.user.id))
    prompt_orm = await UserPrompts(user=user_orm).create(user_prompt_create_input, db)
    return prompt_orm


@router.get("/")
async def list_prompts(user_res: gotrue.UserResponse = Depends(get_user_from_access_token)):
    pass


@router.get("/{id}")
async def get_prompt(id: str, user_res: gotrue.UserResponse = Depends(get_user_from_access_token)):
    pass


@router.put("/{id}")
async def update_prompt(user_res: gotrue.UserResponse = Depends(get_user_from_access_token)):
    pass


@router.delete("/{id}")
async def delete_prompt(user_res: gotrue.UserResponse = Depends(get_user_from_access_token)):
    pass


@router.get("/{id}/run/{input}")
async def run_prompt(user_res: gotrue.UserResponse = Depends(get_user_from_access_token)):
    pass
