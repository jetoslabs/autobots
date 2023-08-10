from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from autobots.conn.openai.chat import Message, Role, ChatReq
from autobots.conn.openai.openai import get_openai
from autobots.database.base import get_db
from autobots.prompts.prompt_crud import PromptCRUD
from autobots.prompts.prompt_orm_model import PromptORM
from autobots.prompts.target_platform import LLMTargetPlatform
from autobots.user.user_orm_model import UserORM


class UserPromptCreateInput(BaseModel):
    name: str
    chat_req: ChatReq
    target_platform: LLMTargetPlatform
    version: Optional[float]
    description: Optional[str]


class UserPromptCreateOutput(UserPromptCreateInput):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Input(BaseModel):
    input: str


class UserPrompts:

    def __init__(self, user: UserORM):
        self.user = user

    async def create(
            self, user_prompt_create_input: UserPromptCreateInput, db: Session = next(get_db())
    ) -> PromptORM:
        prompt = PromptORM(user_id=self.user.id, **user_prompt_create_input.__dict__)
        prompt_orm: PromptORM = await PromptCRUD.create(prompt, db)
        return prompt_orm

    async def list(
            self, limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
    ) -> List[PromptORM]:
        if limit < 0 or limit > 100:
            limit = 100
        if offset < 0:
            offset = 0
        prompts = await PromptCRUD.list(self.user.id, limit, offset, db)
        return prompts

    async def read(self, id: UUID, db: Session = Depends(get_db)) -> PromptORM:
        prompt = await PromptCRUD.read(self.user.id, id, db)
        return prompt

    async def delete(self, id: UUID, db: Session = Depends(get_db)) -> PromptORM:
        existing_prompt = await self.read(id, db)
        if self.user.id != existing_prompt.user_id:
            raise HTTPException(405, "User does not own prompt")
        prompt_orm: PromptORM = await PromptCRUD.delete(existing_prompt, db)
        return prompt_orm

    async def upsert(
            self, id: UUID, user_prompt_create_input: UserPromptCreateInput, db: Session = Depends(get_db)
    ) -> PromptORM:
        existing_prompt = await self.read(id, db)
        if self.user.id != existing_prompt.user_id:
            raise HTTPException(405, "User does not own prompt")
        new_prompt = PromptORM(user_id=self.user.id, **user_prompt_create_input.__dict__)
        prompt_orm: PromptORM = await PromptCRUD.upsert(existing_prompt, new_prompt, db)
        return prompt_orm

    async def run(self, id: UUID, input: Input, db: Session = Depends(get_db)) -> Message | None:
        user_message = Message(role=Role.user, content=input.input)
        prompt_orm = await self.read(id, db)
        if prompt_orm.target_platform.lower() == LLMTargetPlatform.openai:
            chat_req = ChatReq(**prompt_orm.chat_req)
            chat_req.messages = chat_req.messages + [user_message]
            chat_res = await get_openai().chat(chat_req=chat_req)
            resp = chat_res.choices[0].message
            return resp

    async def read_by_name_version(
            self, name: str, version: str = None, limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
    ) -> List[PromptORM]:
        prompts = await PromptCRUD.read_by_name_version(self.user.id, name, version, limit, offset, db)
        return prompts
