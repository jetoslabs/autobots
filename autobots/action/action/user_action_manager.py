from functools import lru_cache
from typing import Any, Dict

from fastapi import HTTPException, BackgroundTasks

from autobots.action.action.action_doc_model import ActionDoc
from autobots.action.action_result.action_result_doc_model import ActionResultDoc, ActionResultCreate, \
    ActionResultStatus
from autobots.action.action_result.user_action_result import UserActionResult
from autobots.action.action_type.abc.IAction import IAction, ActionInputType
from autobots.action.action_type.action_text2img.action_text2img_dalle_openai_v2 import ActionGenImageDalleOpenAiV2
from autobots.action.action_type.action_text2img.action_text2img_stability_ai_v2 import ActionGenImageStabilityAiV2
from autobots.action.action_type.action_text2text.action_text2text_llm_chat_openai_v2 import ActionGenTextLlmChatOpenaiV2
from autobots.action.action_type.action_text2text.action_text2text_llm_chat_with_vector_search_openai import \
    ActionGenTextLlmChatWithVectorSearchOpenai, ActionCreateGenTextLlmChatWithVectorSearchOpenai
from autobots.action.action_type.action_img2img.action_image_mixer_stable_diffusion import \
    ActionImageMixerStableDiffusion, ImageMixerRunModel
from autobots.action.action_type.action_text2img.action_text2img_stable_diffusion import ActionText2ImgStableDiffusion, \
    Text2ImgRunModel
from autobots.action.action_type.action_text2video.action_text2video_stable_diffusion import \
    ActionText2VideoStableDiffusion, Text2VideoRunModel
from autobots.action.action_type.action_types import ActionType
from autobots.action.action.common_action_models import TextObj, TextObjs
from autobots.conn.openai.chat import ChatReq
from autobots.conn.openai.image_model import ImageReq
from autobots.conn.stability.stability_data import StabilityReq
from autobots.conn.stable_diffusion.image_mixer.image_mixer_model import ImageMixerReqModel
from autobots.conn.stable_diffusion.text2img.text2img_model import Text2ImgReqModel
from autobots.conn.stable_diffusion.text2video.text2video_model import Text2VideoReqModel
from autobots.core.log import log


class UserActionManager:

    def __init__(self):
        pass

    @staticmethod
    @lru_cache
    def get_action_types():
        action_types = [action_type for action_type in ActionType]
        return action_types

    async def run_action(
            self, action: ActionDoc, action_input: Dict[str, Any]
    ) -> Any | TextObjs:
        match action.type:
            case ActionType.text2text_llm_chat_openai:
                return await ActionGenTextLlmChatOpenaiV2.run_action_doc(action, action_input)
            case ActionType.text2img_dalle_openai:
                return await ActionGenImageDalleOpenAiV2.run_action_doc(action, action_input)
            case ActionType.text2img_stability_ai:
                return await ActionGenImageStabilityAiV2.run_action_doc(action, action_input)
            case ActionType.text2text_llm_chat_with_vector_search_openai:
                return await ActionGenTextLlmChatWithVectorSearchOpenai.run_action_doc(action, action_input)
            case ActionType.text2img_stable_diffusion:
                return await ActionText2ImgStableDiffusion.run_action_doc(action, action_input)
            case ActionType.image_mixer_stable_diffusion:
                return await ActionImageMixerStableDiffusion.run_action_doc(action, action_input)
            case ActionType.text2video_stable_diffusion:
                return await ActionText2VideoStableDiffusion.run_action_doc(action, action_input)
            case _:
                log.error("Action Type not found")
                raise HTTPException(status_code=404, detail="Action Type not found")

    async def get_action(self, action_doc: ActionDoc) -> IAction:
        match action_doc.type:
            case ActionType.text2text_llm_chat_openai:
                return ActionGenTextLlmChatOpenaiV2(ChatReq.model_validate(action_doc.config))
            case ActionType.text2img_dalle_openai:
                return ActionGenImageDalleOpenAiV2(ImageReq.model_validate(action_doc.config))
            case ActionType.text2img_stability_ai:
                return ActionGenImageStabilityAiV2(StabilityReq.model_validate(action_doc.config))
            case ActionType.text2text_llm_chat_with_vector_search_openai:
                return ActionGenTextLlmChatWithVectorSearchOpenai(ActionCreateGenTextLlmChatWithVectorSearchOpenai.model_validate(action_doc.model_dump()))
            case ActionType.text2img_stable_diffusion:
                return ActionText2ImgStableDiffusion(Text2ImgReqModel.model_validate(action_doc.model_dump()))
            case ActionType.image_mixer_stable_diffusion:
                return ActionImageMixerStableDiffusion(ImageMixerReqModel.model_validate(action_doc.model_dump()))
            case ActionType.text2video_stable_diffusion:
                return ActionText2VideoStableDiffusion(Text2VideoReqModel.model_validate(action_doc.model_dump()))
            case _:
                log.error("Action Type not found")
                raise HTTPException(status_code=404, detail="Action Type not found")

    async def get_action_input(self, action_doc: ActionDoc, action_input: Dict[str, Any]) -> ActionInputType:
        match action_doc.type:
            case ActionType.text2text_llm_chat_openai:
                return await ActionGenTextLlmChatOpenaiV2.action_input_dict_to_type(action_input)
            case ActionType.text2img_dalle_openai:
                return await ActionGenImageDalleOpenAiV2.action_input_dict_to_type(action_input)
            case ActionType.text2img_stability_ai:
                return await ActionGenImageStabilityAiV2.action_input_dict_to_type(action_input)
            case ActionType.text2text_llm_chat_with_vector_search_openai:
                return await ActionGenTextLlmChatWithVectorSearchOpenai.action_input_dict_to_type(action_input)
            case ActionType.text2img_stable_diffusion:
                return await ActionText2ImgStableDiffusion.action_input_dict_to_type(action_input)
            case ActionType.image_mixer_stable_diffusion:
                return await ActionImageMixerStableDiffusion.action_input_dict_to_type(action_input)
            case ActionType.text2video_stable_diffusion:
                return await ActionText2VideoStableDiffusion.action_input_dict_to_type(action_input)
            case _:
                log.error("Action Type not found")
                raise HTTPException(status_code=404, detail="Action Type not found")

    async def run_action_in_background(
            self,
            action_doc: ActionDoc,
            action_input: Dict[str, Any],
            user_action_result: UserActionResult,
            background_tasks: BackgroundTasks
    ) -> ActionResultDoc:
        action: IAction = await self.get_action(action_doc)
        action_input = await self.get_action_input(action_doc, action_input)
        return await action.run_action_in_background(action_doc, action_input, user_action_result, background_tasks)
