from typing import List
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from autobots.auth.security import get_user_from_access_token
from autobots.conn.openai.chat import Message
from autobots.core.log import log
from autobots.database.base import get_db
from autobots.database.database_models import UserORM
from autobots.user.user_prompts import UserPrompts, UserPromptCreateInput, UserPromptCreateOutput, Input

router = APIRouter()


@router.post("/")
async def create_prompt(
        user_prompt_create_input: UserPromptCreateInput,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Session = Depends(get_db)
) -> UserPromptCreateOutput:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        prompt_orm = await UserPrompts(user=user_orm).create(user_prompt_create_input, db)
        output = UserPromptCreateOutput.model_validate(prompt_orm)
        return output
    except IntegrityError as ie:
        log.error(ie)
        raise HTTPException(400, "Name and version is not unique")
    except Exception as e:
        log.error(e)
        raise HTTPException(500)


@router.get("/")
async def list_prompts(
        limit: int = 100, offset: int = 0,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Session = Depends(get_db)
) -> List[UserPromptCreateOutput]:
    user_orm = UserORM(id=UUID(user_res.user.id))
    prompt_orm_s = await UserPrompts(user=user_orm).list(limit, offset, db)
    output = [UserPromptCreateOutput.model_validate(prompt_orm) for prompt_orm in prompt_orm_s]
    return output


@router.get("/{id}")
async def get_prompt(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Session = Depends(get_db)
) -> UserPromptCreateOutput:
    user_orm = UserORM(id=UUID(user_res.user.id))
    prompt_orm = await UserPrompts(user=user_orm).read(UUID(id), db)
    output = UserPromptCreateOutput.model_validate(prompt_orm)
    return output


@router.put("/{id}")
async def replace_prompt(
        id: str,
        user_prompt_create_input: UserPromptCreateInput,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Session = Depends(get_db)
) -> UserPromptCreateOutput:
    user_orm = UserORM(id=UUID(user_res.user.id))
    prompt_orm = await UserPrompts(user=user_orm).upsert(UUID(id), user_prompt_create_input, db)
    output = UserPromptCreateOutput.model_validate(prompt_orm)
    return output


@router.delete("/{id}")
async def delete_prompt(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Session = Depends(get_db)
) -> UserPromptCreateOutput:
    user_orm = UserORM(id=UUID(user_res.user.id))
    prompt_orm = await UserPrompts(user=user_orm).delete(UUID(id), db)
    output = UserPromptCreateOutput.model_validate(prompt_orm)
    return output


@router.post("/{id}/run/")
async def run_prompt(
        id: str,
        input: Input,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Session = Depends(get_db)
) -> Message:
    user_orm = UserORM(id=UUID(user_res.user.id))
    message = await UserPrompts(user=user_orm).run(UUID(id), input, db)
    return message


@router.get("/name/{name}/version/{version}")
async def get_prompt(
        name: str, version: str = None,
        limit: int = 100, offset: int = 0,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Session = Depends(get_db)
) -> List[UserPromptCreateOutput]:
    user_orm = UserORM(id=UUID(user_res.user.id))
    prompt_orm_s = await UserPrompts(user=user_orm).read_by_name_version(name, version, limit, offset, db)
    output = [UserPromptCreateOutput.model_validate(prompt_orm) for prompt_orm in prompt_orm_s]
    return output
