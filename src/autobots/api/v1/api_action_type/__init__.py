from fastapi import APIRouter

from src.autobots import SettingsProvider
from src.autobots.api.v1.api_action_type.audio2text import api_actions_audio2text_transcription_openai
from src.autobots.api.v1.api_action_type.audio2text import api_actions_audio2text_translation_openai
from src.autobots.api.v1.api_action_type.img2img import api_actions_img2img_edit_openai, image_mixer_stable_diffusion, \
    api_actions_img2img_variation_openai
from src.autobots.api.v1.api_action_type.multimodal import api_actions_multimodal
from src.autobots.api.v1.api_action_type.text2audio import api_actions_text2audio_speech_openai
from src.autobots.api.v1.api_action_type.text2img import api_actions_text2img_stable_diffusion
from src.autobots.api.v1.api_action_type.text2img import api_actions_text2img_stability_ai, api_actions_text2img_openai
from src.autobots.api.v1.api_action_type.text2text import api_actions_text2text
from src.autobots.api.v1.api_action_type.text2video import api_actions_text2video_stable_diffusion

prefix = SettingsProvider.sget().API_ACTION_TYPES
router = APIRouter(prefix=prefix)

# multimodal
router.include_router(api_actions_multimodal.router, tags=[f"{prefix}/multimodal"])
# text2text
router.include_router(api_actions_text2text.router, tags=[f"{prefix}/text2text"])
# text2img
router.include_router(api_actions_text2img_openai.router, tags=[f"{prefix}/text2img"])
router.include_router(api_actions_text2img_stable_diffusion.router, tags=[f"{prefix}/text2img"])
router.include_router(api_actions_text2img_stability_ai.router, tags=[f"{prefix}/text2img"])
# img2img
router.include_router(image_mixer_stable_diffusion.router, tags=[f"{prefix}/img2img"])
router.include_router(api_actions_img2img_edit_openai.router, tags=[f"{prefix}/img2img"])
router.include_router(api_actions_img2img_variation_openai.router, tags=[f"{prefix}/img2img"])
# text2video
router.include_router(api_actions_text2video_stable_diffusion.router, tags=[f"{prefix}/text2video"])
# text2audio
router.include_router(api_actions_text2audio_speech_openai.router, tags=[f"{prefix}/text2audio"])
# audio2text
router.include_router(api_actions_audio2text_transcription_openai.router, tags=[f"{prefix}/audio2text"])
router.include_router(api_actions_audio2text_translation_openai.router, tags=[f"{prefix}/audio2text"])
