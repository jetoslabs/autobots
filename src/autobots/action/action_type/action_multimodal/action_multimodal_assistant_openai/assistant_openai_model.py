from openai.types.beta import Assistant

from src.autobots.conn.openai.openai_assistants.assistant_model import AssistantCreate, AssistantUpdate


class AssistantOpenaiConfigCreate(AssistantCreate):
    pass


class AssistantOpenaiConfigUpdate(AssistantUpdate):
    pass


class AssistantOpenaiConfig(Assistant):
    pass