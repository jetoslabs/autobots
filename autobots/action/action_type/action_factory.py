from functools import lru_cache
from typing import List, Any, Dict

from fastapi import HTTPException, BackgroundTasks

from autobots.action.action.action_doc_model import ActionDoc
from autobots.action.action.common_action_models import TextObj
from autobots.action.action_result.action_result_doc_model import ActionResultDoc, ActionResultCreate, ActionResultUpdate
from autobots.action.action_result.user_action_result import UserActionResult
from autobots.action.action_type.action_img2img.action_image_mixer_stable_diffusion import \
    ActionImageMixerStableDiffusion
from autobots.action.action_type.action_mock.action_mock import MockAction
from autobots.action.action_type.action_text2img.action_text2img_dalle_openai_v2 import ActionGenImageDalleOpenAiV2
# from autobots.action.action_type.action_text2img.action_text2img_stability_ai_v2 import ActionGenImageStabilityAiV2
from autobots.action.action_type.action_text2img.action_text2img_stable_diffusion import ActionText2ImgStableDiffusion
from autobots.action.action_type.action_text2text.action_text2text_llm_chat_openai_v2 import \
    ActionGenTextLlmChatOpenaiV2
from autobots.action.action_type.action_text2text.action_text2text_llm_chat_with_vector_search_openai import \
    ActionGenTextLlmChatWithVectorSearchOpenai
from autobots.action.action_type.action_text2video.action_text2video_stable_diffusion import \
    ActionText2VideoStableDiffusion
from autobots.action.action_type.action_types import ActionType
from autobots.core.log import log
from autobots.event_result.event_result_model import EventResultStatus


class ActionFactory:

    @staticmethod
    @lru_cache
    def get_action_types() -> List[str]:
        action_types = [action_type for action_type in ActionType if not action_type.lower().startswith("mock")]
        return action_types

    async def run_action(self, action_doc: ActionDoc, action_input_dict: Dict[str, Any]) -> Any:
        match action_doc.type:
            case ActionType.text2text_llm_chat_openai:
                config = ActionGenTextLlmChatOpenaiV2.get_config_type().model_validate(action_doc.config)
                input = ActionGenTextLlmChatOpenaiV2.get_input_type().model_validate(action_input_dict)
                return await ActionGenTextLlmChatOpenaiV2(config).run_action(input)

            case ActionType.text2img_dalle_openai:
                config = ActionGenImageDalleOpenAiV2.get_config_type().model_validate(action_doc.config)
                input = ActionGenImageDalleOpenAiV2.get_input_type().model_validate(action_input_dict)
                return await ActionGenImageDalleOpenAiV2(config).run_action(input)

            # case ActionType.text2img_stability_ai:
            #     config = ActionGenImageStabilityAiV2.get_config_type().model_validate(action_doc.config)
            #     input = ActionGenImageStabilityAiV2.get_input_type().model_validate(action_input_dict)
            #     return await ActionGenImageStabilityAiV2(config).run_action(input)

            case ActionType.text2text_llm_chat_with_vector_search_openai:
                config = ActionGenTextLlmChatWithVectorSearchOpenai.get_config_type().model_validate(action_doc.config)
                input = ActionGenTextLlmChatWithVectorSearchOpenai.get_input_type().model_validate(action_input_dict)
                return await ActionGenTextLlmChatWithVectorSearchOpenai(config).run_action(input)

            case ActionType.text2img_stable_diffusion:
                config = ActionText2ImgStableDiffusion.get_config_type().model_validate(action_doc.config)
                input = ActionText2ImgStableDiffusion.get_input_type().model_validate(action_input_dict)
                return await ActionText2ImgStableDiffusion(config).run_action(input)

            case ActionType.image_mixer_stable_diffusion:
                config = ActionImageMixerStableDiffusion.get_config_type().model_validate(action_doc.config)
                input = ActionImageMixerStableDiffusion.get_input_type().model_validate(action_input_dict)
                return await ActionImageMixerStableDiffusion(config).run_action(input)

            case ActionType.text2video_stable_diffusion:
                config = ActionText2VideoStableDiffusion.get_config_type().model_validate(action_doc.config)
                input = ActionText2VideoStableDiffusion.get_input_type().model_validate(action_input_dict)
                return await ActionText2VideoStableDiffusion(config).run_action(input)

            case ActionType.mock_action:
                config = MockAction.get_config_type().model_validate(action_doc.config)
                input = MockAction.get_input_type().model_validate(action_doc.input)
                return await MockAction(config).run_action(input)

            case _:
                log.error("Action Type not found")
                raise HTTPException(status_code=404, detail="Action Type not found")

    async def run_action_in_background(
            self,
            action_doc: ActionDoc,
            action_input_dict: Dict[str, Any],
            user_action_result: UserActionResult,
            background_tasks: BackgroundTasks = None
    ) -> ActionResultDoc | None:
        # Create initial Action Result
        action_doc.input = action_input_dict
        action_result_create: ActionResultCreate = ActionResultCreate(
            status=EventResultStatus.processing, result=action_doc, is_saved=False
        )
        action_result_doc = await user_action_result.create_action_result(action_result_create)
        # Run Action in background and update the Action Result with Output
        if background_tasks:
            # Run in background
            background_tasks.add_task(
                self._run_action_as_background_task, action_input_dict, action_result_doc, user_action_result
            )
        else:
            # For testing
            await self._run_action_as_background_task(
                action_input_dict, action_result_doc, user_action_result
            )
        return action_result_doc

    async def _run_action_as_background_task(
            self,
            action_input_dict: Dict[str, Any],
            action_result_doc: ActionResultDoc,
            user_action_result: UserActionResult
    ) -> None:
        try:
            # Run the action
            result = await self.run_action(action_result_doc.result, action_input_dict)
            # Action is a success
            action_result_doc.status = EventResultStatus.success
            action_result_doc.result.output = result
            log.bind(action_result_doc=action_result_doc).info("Action run success")
        except Exception as e:
            # Action resulted in an error
            action_result_doc.status = EventResultStatus.error
            action_result_doc.error_message = TextObj(text="Action run error")
            log.bind(action_result_doc=action_result_doc, error=e).error("Action run error")
        finally:
            # Finally persist the Action Result
            action_result_update = ActionResultUpdate(**action_result_doc.model_dump())
            action_result_doc = await user_action_result.update_action_result(
                action_result_doc.id,
                action_result_update
            )
            log.bind(action_result_doc=action_result_doc).info("Action Result updated")






