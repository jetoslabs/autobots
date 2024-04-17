from openai.types.beta import Assistant

from src.autobots.conn.openai.openai_assistants.assistant_model import AssistantCreate


class AssistantOpenaiConfigCreate(AssistantCreate):
    pass


# TODO: being this back, with parent field assistant_id removed
# class AssistantOpenaiConfigUpdate(AssistantUpdate):
#     pass

class AssistantOpenaiConfigUpdate(AssistantCreate):
    pass


class AssistantOpenaiConfig(Assistant):
    pass
