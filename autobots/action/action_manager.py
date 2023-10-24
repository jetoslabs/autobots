from functools import lru_cache
from typing import Any

from fastapi import HTTPException

from autobots.action.action_doc_model import ActionDoc
from autobots.action.action_type.action_text2img.action_gen_image_dalle_openai_v2 import ActionGenImageDalleOpenAiV2
from autobots.action.action_type.action_text2img.action_gen_image_stability_ai_v2 import ActionGenImageStabilityAiV2
from autobots.action.action_type.action_text2text.action_gen_text_llm_chat_openai_v2 import ActionGenTextLlmChatOpenaiV2
from autobots.action.action_type.action_text2text.action_gen_text_llm_chat_with_vector_search_openai import \
    ActionGenTextLlmChatWithVectorSearchOpenai, ActionCreateGenTextLlmChatWithVectorSearchOpenai
from autobots.action.action_type.action_img2img.action_image_mixer_stable_diffusion import \
    ActionImageMixerStableDiffusion, ImageMixerRunModel
from autobots.action.action_type.action_text2img.action_text2img_stable_diffusion import ActionText2ImgStableDiffusion, \
    Text2ImgRunModel
from autobots.action.action_type.action_text2video.action_text2video_stable_diffusion import \
    ActionText2VideoStableDiffusion, Text2VideoRunModel
from autobots.action.action_type.action_types import ActionType
from autobots.action.common_action_models import TextObj
from autobots.conn.openai.chat import ChatReq
from autobots.conn.openai.image_model import ImageReq
from autobots.conn.stability.stability_data import StabilityReq
from autobots.conn.stable_diffusion.image_mixer.image_mixer_model import ImageMixerReqModel
from autobots.conn.stable_diffusion.text2img.text2img_model import Text2ImgReqModel
from autobots.conn.stable_diffusion.text2video.text2video_model import Text2VideoReqModel
from autobots.core.log import log


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
            action_input: TextObj | Text2ImgRunModel | ImageMixerRunModel | Text2VideoRunModel
    ) -> Any:
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
            case ActionType.text2img_stable_diffusion:
                return await ActionText2ImgStableDiffusion(Text2ImgReqModel.model_validate(action.model_dump())
                                                           ).run_action(action_input)
            case ActionType.image_mixer_stable_diffusion:
                return await ActionImageMixerStableDiffusion(ImageMixerReqModel.model_validate(action.model_dump())
                                                           ).run_action(action_input)
            case ActionType.text2video_stable_diffusion:
                return await ActionText2VideoStableDiffusion(Text2VideoReqModel.model_validate(action.model_dump())
                                                           ).run_action(action_input)
            case _:
                log.error("Action Type not found")
                raise HTTPException(status_code=404, detail="Action Type not found")
