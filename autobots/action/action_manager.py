from functools import lru_cache
from typing import Any

from autobots.action.action_doc_model import ActionDoc
from autobots.action.action_gen_image_dalle_openai import ActionGenImageDalleOpenai
from autobots.action.action_gen_image_stability_ai import ActionGenImageStabilityAi
from autobots.action.action_gen_text_llm_chat_openai import ActionGenTextLlmChatOpenai
from autobots.action.action_types import ActionType
from autobots.core.log import log
from autobots.prompts.user_prompts import Input


class ActionManager:

    def __init__(self):
        pass

    @staticmethod
    @lru_cache
    def get_action_types():
        action_types = [action_type for action_type in ActionType]
        return action_types

    async def run_action(self, action: ActionDoc, action_input: Input) -> Any:
        match action.type:
            case ActionType.gen_text_llm_chat_openai:
                return await ActionGenTextLlmChatOpenai.run(action, action_input)
            case ActionType.gen_image_dalle_openai:
                return await ActionGenImageDalleOpenai.run(action, action_input)
            case ActionType.gen_image_stability_ai:
                return await ActionGenImageStabilityAi.run(action, action_input)
            case _:
                log.error("Action Type not found")
