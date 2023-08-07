from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import Session

from autobots.conn.openai.chat import Message
from autobots.conn.openai.openai import get_openai
from autobots.database.base import get_db
from autobots.database.database_models import UserORM, PromptORM
from autobots.database.prompt_crud import PromptCRUD
from autobots.database.target_platform import LLMTargetPlatform
from autobots.llm.llm import LLM


class UserPromptCreateInput(BaseModel):
    name: str
    messages: List[Message]
    target_platform: LLMTargetPlatform
    version: Optional[float]
    description: Optional[str]


class UserPromptCreateOutput(UserPromptCreateInput):
    id: UUID
    created_at: datetime


class UserPrompts:

    def __init__(self, user: UserORM):
        self.user = user

    async def create(
            self, user_prompt_create_input: UserPromptCreateInput, db: Session = next(get_db())
    ) -> PromptORM:
        prompt = PromptORM(user_id=self.user.id, **user_prompt_create_input.__dict__)
        prompt_orm: PromptORM = await PromptCRUD.create(prompt, db)
        return prompt_orm

    @staticmethod
    async def test(messages: List[Message], target_platform: LLMTargetPlatform) -> Message | None:
        if target_platform.lower() == LLMTargetPlatform.openai:
            resp = await LLM.chat_openai(messages, llm=get_openai())
            return resp

    async def read_by_name(self, name: str) -> list[PromptORM]:
        prompts = await PromptCRUD.read_by_name(self.user.id, name)
        return prompts

    async def read(self, id: UUID) -> PromptORM:
        prompts = await PromptCRUD.read(self.user.id, id)
        return prompts[0]
