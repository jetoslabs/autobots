from typing import Iterable

from openai.types.beta import Assistant, AssistantToolParam

from src.autobots.conn.openai.openai_assistants.assistant_model import AssistantCreate


class AssistantOpenaiConfigCreate(AssistantCreate):
    tools: Iterable[AssistantToolParam | str] | None = None


# TODO: being this back, with parent field assistant_id removed
# class AssistantOpenaiConfigUpdate(AssistantUpdate):
#     pass

class AssistantOpenaiConfigUpdate(AssistantCreate):
    tools: Iterable[AssistantToolParam | str] | None = None


class AssistantOpenaiConfig(Assistant):
    pass
