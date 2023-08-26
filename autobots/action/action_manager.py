from functools import lru_cache
from typing import Any, List

from autobots.action.action_doc_model import ActionDoc
from autobots.action.action_types import ActionType
from autobots.conn.openai.chat import ChatReq, Message, Role
from autobots.conn.openai.image_model import ImageReq, ImageRes
from autobots.conn.openai.openai import get_openai
from autobots.conn.stability.stability import get_stability
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

    async def run_action(
            self,
            action: ActionDoc,
            action_input: Input
    ) -> Any:
        match action.type:
            case ActionType.gen_text_llm_chat_openai:
                return await self._run_gen_text_llm_chat_openai(action, action_input)
            case ActionType.gen_image_dalle_openai:
                return await self._run_gen_image_dalle_openai(action, action_input)
            case ActionType.gen_image_stability_ai:
                return await self._run_gen_image_stability_ai(action, action_input)
            case _:
                log.error("Action Type not found")

    async def _run_gen_text_llm_chat_openai(self, action: ActionDoc, action_input: Input) -> Message:
        chat_req = ChatReq.model_validate(action.input)
        message = Message(role=Role.user, content=action_input.input)
        chat_req.messages = chat_req.messages + [message]
        chat_res = await get_openai().chat(chat_req=chat_req)
        resp = chat_res.choices[0].message
        return resp

    async def _run_gen_image_dalle_openai(self, action: ActionDoc, action_input: Input) -> List[ImageRes]:
        image_req = ImageReq.model_validate(action.input)
        image_req.prompt = action_input.input
        images = await get_openai().create_image(image_req)
        return images

    async def _run_gen_image_stability_ai(self,  action: ActionDoc, action_input: Input) -> List[ImageRes]:
        stability_req = StabilityReq.model_validate(action.input)
        stability_req.prompt = action_input.input
        file_url = await get_stability().text_to_image(stability_req)
        resp = [ImageRes(url=file_url.unicode_string())]
        return resp




