from openai import AsyncOpenAI
from openai.types.beta import Assistant

from autobots.conn.openai.openai_assistant.assistant_model import AssistantCreate
from autobots.core.logging.log import Log


class OpenaiAssistant():

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

    async def create(self, assistant_create: AssistantCreate) -> Assistant | None:
        try:
            return await self.client.beta.assistants.create(**assistant_create.model_dump(exclude_none=True))
        except Exception as e:
            Log.error(str(e))

    async def create(self, assistant_create: AssistantCreate) -> Assistant | None:
        try:
            return await self.client.beta.assistants.create(**assistant_create.model_dump(exclude_none=True))
        except Exception as e:
            Log.error(str(e))
