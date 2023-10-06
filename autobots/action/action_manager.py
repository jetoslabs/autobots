from functools import lru_cache
from typing import Any

from fastapi import HTTPException

from autobots.action.action_doc_model import ActionDoc
from autobots.action.action_gen_image_dalle_openai_v2 import ActionGenImageDalleOpenAiV2
from autobots.action.action_gen_image_stability_ai_v2 import ActionGenImageStabilityAiV2
from autobots.action.action_gen_text_llm_chat_openai_v2 import ActionGenTextLlmChatOpenaiV2
from autobots.action.action_gen_text_llm_chat_with_vector_search_openai import \
    ActionGenTextLlmChatWithVectorSearchOpenai, ActionCreateGenTextLlmChatWithVectorSearchOpenai
from autobots.action.action_types import ActionType
from autobots.conn.openai.chat import ChatReq
from autobots.conn.openai.image_model import ImageReq
from autobots.conn.stability.stability_data import StabilityReq
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
                return await ActionGenTextLlmChatOpenaiV2(ChatReq.model_validate(action.config))\
                    .run_action(action_input)
            case ActionType.gen_image_dalle_openai:
                return await ActionGenImageDalleOpenAiV2(ImageReq.model_validate(action.config))\
                    .run_action(action_input)
            case ActionType.gen_image_stability_ai:
                return await ActionGenImageStabilityAiV2(StabilityReq.model_validate(action.config))\
                    .run_action(action_input)
            case ActionType.gen_text_llm_chat_with_vector_search_openai:
                return await ActionGenTextLlmChatWithVectorSearchOpenai(
                    ActionCreateGenTextLlmChatWithVectorSearchOpenai.model_validate(action.model_dump())
                ).run_action(action_input)
            case _:
                log.error("Action Type not found")
                raise HTTPException(status_code=404, detail="Action Type not found")
