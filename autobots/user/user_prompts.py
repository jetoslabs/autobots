from typing import List

from sqlalchemy import UUID

from autobots.conn.openai.chat import Message
from autobots.conn.openai.openai import get_openai
from autobots.database.database_models import UserORM, PromptORM
from autobots.database.prompt_crud import PromptCRUD
from autobots.database.target_platform import LLMTargetPlatform
from autobots.llm.llm import LLM


class UserPrompts:

    def __init__(self, user: UserORM):
        # super().__init__()
        self.user = user

    async def create(self, name: str, messages: List[Message], target_platform: LLMTargetPlatform, description: str | None = None):
        prompt = PromptORM(
            name=name,
            prompt=messages,
            user_id=self.user.id,
            target_platform=target_platform,
            description=description)
        await PromptCRUD.create(prompt)

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
