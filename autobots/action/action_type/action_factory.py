from functools import lru_cache
from typing import List, Any, Dict

from fastapi import HTTPException, BackgroundTasks

from autobots.action.action.action_doc_model import ActionDoc
from autobots.action.action.common_action_models import TextObj
from autobots.action.action_result.action_result_doc_model import ActionResultDoc, ActionResultCreate, ActionResultUpdate
from autobots.action.action_result.user_action_result import UserActionResult
from autobots.action.action_type.action_audio2text.action_audio2text_transcription_openai import ActionAudio2TextTranscriptionOpenai
from autobots.action.action_type.action_audio2text.action_audio2text_translation_openai import \
    ActionAudio2TextTranslationOpenai
from autobots.action.action_type.action_img2img.action_image_mixer_stable_diffusion import \
    ActionImageMixerStableDiffusion
from autobots.action.action_type.action_img2img.action_img2img_edit_openai import ActionImg2ImgEditOpenai
from autobots.action.action_type.action_img2img.action_img2img_stable_diffusion import ActionImg2ImgStableDiffusion
from autobots.action.action_type.action_img2img.action_img2img_variation_openai import ActionImg2ImgVariationOpenai
from autobots.action.action_type.action_mock.action_mock import MockAction
from autobots.action.action_type.action_text2audio.action_text2audio_speech_openai import ActionText2AudioSpeechOpenai
from autobots.action.action_type.action_text2img.action_text2img_dalle_openai_v2 import ActionGenImageDalleOpenAiV2
# from autobots.action.action_type.action_text2img.action_text2img_stability_ai_v2 import ActionGenImageStabilityAiV2
from autobots.action.action_type.action_text2img.action_text2img_stable_diffusion import ActionText2ImgStableDiffusion
from autobots.action.action_type.action_text2text.action_text2text_llm_chat_openai_v2 import \
    ActionText2TextLlmChatOpenai
from autobots.action.action_type.action_text2text.action_text2text_llm_chat_with_vector_search_openai import \
    ActionText2TextLlmChatWithVectorSearchOpenai
from autobots.action.action_type.action_text2text.action_text2text_read_url import ActionText2TextReadUrl
from autobots.action.action_type.action_text2text.action_text2text_search_web import ActionText2TextSearchWeb
from autobots.action.action_type.action_text2video.action_text2video_stable_diffusion import \
    ActionText2VideoStableDiffusion
from autobots.action.action_type.action_types import ActionType
from autobots.api.webhook import Webhook
from autobots.core.logging.log import Log
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
                config = ActionText2TextLlmChatOpenai.get_config_type().model_validate(action_doc.config)
                input = ActionText2TextLlmChatOpenai.get_input_type().model_validate(action_input_dict)
                return await ActionText2TextLlmChatOpenai(config).run_action(input)

            case ActionType.text2img_dalle_openai:
                config = ActionGenImageDalleOpenAiV2.get_config_type().model_validate(action_doc.config)
                input = ActionGenImageDalleOpenAiV2.get_input_type().model_validate(action_input_dict)
                return await ActionGenImageDalleOpenAiV2(config).run_action(input)

            # case ActionType.text2img_stability_ai:
            #     config = ActionGenImageStabilityAiV2.get_config_type().model_validate(action_doc.config)
            #     input = ActionGenImageStabilityAiV2.get_input_type().model_validate(action_input_dict)
            #     return await ActionGenImageStabilityAiV2(config).run_action(input)

            case ActionType.text2text_llm_chat_with_vector_search_openai:
                config = ActionText2TextLlmChatWithVectorSearchOpenai.get_config_type().model_validate(action_doc.config)
                input = ActionText2TextLlmChatWithVectorSearchOpenai.get_input_type().model_validate(action_input_dict)
                return await ActionText2TextLlmChatWithVectorSearchOpenai(config).run_action(input)

            case ActionType.text2text_read_url:
                config = ActionText2TextReadUrl.get_config_type().model_validate(
                    action_doc.config)
                input = ActionText2TextReadUrl.get_input_type().model_validate(action_input_dict)
                return await ActionText2TextReadUrl(config).run_action(input)

            case ActionType.text2text_search_web:
                config = ActionText2TextSearchWeb.get_config_type().model_validate(
                    action_doc.config)
                input = ActionText2TextSearchWeb.get_input_type().model_validate(action_input_dict)
                return await ActionText2TextSearchWeb(config).run_action(input)

            case ActionType.text2img_stable_diffusion:
                config = ActionText2ImgStableDiffusion.get_config_type().model_validate(action_doc.config)
                input = ActionText2ImgStableDiffusion.get_input_type().model_validate(action_input_dict)
                return await ActionText2ImgStableDiffusion(config).run_action(input)

            case ActionType.img2img_stable_diffusion:
                config = ActionImg2ImgStableDiffusion.get_config_type().model_validate(action_doc.config)
                input = ActionImg2ImgStableDiffusion.get_input_type().model_validate(action_input_dict)
                return await ActionImg2ImgStableDiffusion(config).run_action(input)

            case ActionType.image_mixer_stable_diffusion:
                config = ActionImageMixerStableDiffusion.get_config_type().model_validate(action_doc.config)
                input = ActionImageMixerStableDiffusion.get_input_type().model_validate(action_input_dict)
                return await ActionImageMixerStableDiffusion(config).run_action(input)

            case ActionType.img2img_edit_openai:
                config = ActionImg2ImgEditOpenai.get_config_type().model_validate(action_doc.config)
                input = ActionImg2ImgEditOpenai.get_input_type().model_validate(action_input_dict)
                return await ActionImg2ImgEditOpenai(config).run_action(input)

            case ActionType.img2img_variation_openai:
                config = ActionImg2ImgVariationOpenai.get_config_type().model_validate(action_doc.config)
                input = ActionImg2ImgVariationOpenai.get_input_type().model_validate(action_input_dict)
                return await ActionImg2ImgVariationOpenai(config).run_action(input)

            case ActionType.text2video_stable_diffusion:
                config = ActionText2VideoStableDiffusion.get_config_type().model_validate(action_doc.config)
                input = ActionText2VideoStableDiffusion.get_input_type().model_validate(action_input_dict)
                return await ActionText2VideoStableDiffusion(config).run_action(input)

            case ActionType.text2audio_speech_openai:
                config = ActionText2AudioSpeechOpenai.get_config_type().model_validate(action_doc.config)
                input = ActionText2AudioSpeechOpenai.get_input_type().model_validate(action_input_dict)
                return await ActionText2AudioSpeechOpenai(config).run_action(input)

            case ActionType.audio2text_transcription_openai:
                config = ActionAudio2TextTranscriptionOpenai.get_config_type().model_validate(action_doc.config)
                input = ActionAudio2TextTranscriptionOpenai.get_input_type().model_validate(action_input_dict)
                return await ActionAudio2TextTranscriptionOpenai(config).run_action(input)

            case ActionType.audio2text_translation_openai:
                config = ActionAudio2TextTranslationOpenai.get_config_type().model_validate(action_doc.config)
                input = ActionAudio2TextTranslationOpenai.get_input_type().model_validate(action_input_dict)
                return await ActionAudio2TextTranslationOpenai(config).run_action(input)

            case ActionType.mock_action:
                config = MockAction.get_config_type().model_validate(action_doc.config)
                input = MockAction.get_input_type().model_validate(action_doc.input)
                return await MockAction(config).run_action(input)

            case _:
                Log.error("Action Type not found")
                raise HTTPException(status_code=404, detail="Action Type not found")

    async def run_action_in_background(
            self,
            action_doc: ActionDoc,
            action_input_dict: Dict[str, Any],
            user_action_result: UserActionResult,
            background_tasks: BackgroundTasks = None,
            webhook: Webhook | None = None,
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
                self._run_action_as_background_task, action_input_dict, action_result_doc, user_action_result, webhook
            )
        else:
            # For testing
            await self._run_action_as_background_task(
                action_input_dict, action_result_doc, user_action_result, webhook
            )
        return action_result_doc

    async def _run_action_as_background_task(
            self,
            action_input_dict: Dict[str, Any],
            action_result_doc: ActionResultDoc,
            user_action_result: UserActionResult,
            webhook: Webhook | None = None,
    ) -> None:
        try:
            # Run the action
            result = await self.run_action(action_result_doc.result, action_input_dict)
            # Action is a success
            action_result_doc.status = EventResultStatus.success
            action_result_doc.result.output = result
            Log.bind(action_result_doc=action_result_doc).info("Action run success")
        except Exception as e:
            # Action resulted in an error
            action_result_doc.status = EventResultStatus.error
            action_result_doc.error_message = TextObj(text="Action run error")
            Log.bind(action_result_doc=action_result_doc, error=e).error("Action run error")
        finally:
            # Finally persist the Action Result
            action_result_update = ActionResultUpdate(**action_result_doc.model_dump())
            action_result_doc = await user_action_result.update_action_result(
                action_result_doc.id,
                action_result_update
            )
            Log.bind(action_result_doc=action_result_doc).info("Action Result updated")
            # Send webhook
            if webhook:
                await webhook.send(action_result_doc.model_dump())






