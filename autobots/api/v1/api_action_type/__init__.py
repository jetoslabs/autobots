from fastapi import APIRouter

from autobots import SettingsProvider
from autobots.api.v1.api_action_type.audio2text import api_actions_audio2text_transcription_openai, \
    api_actions_audio2text_translation_openai
from autobots.api.v1.api_action_type.img2img import image_mixer_stable_diffusion
from autobots.api.v1.api_action_type.text2audio import api_actions_text2audio_speech_openai
from autobots.api.v1.api_action_type.text2img import api_actions_text2img_openai, api_actions_text2img_stable_diffusion, \
    api_actions_text2img_stability_ai
from autobots.api.v1.api_action_type.text2text import api_actions_text2text
from autobots.api.v1.api_action_type.text2video import api_actions_text2video_stable_diffusion

prefix = SettingsProvider.sget().API_ACTION_TYPES
router = APIRouter(prefix=prefix)

# text2text
router.include_router(api_actions_text2text.router, tags=[f"{prefix}/text2text"])
# text2img
router.include_router(api_actions_text2img_openai.router, tags=[f"{prefix}/text2img"])
router.include_router(api_actions_text2img_stable_diffusion.router, tags=[f"{prefix}/text2img"])
router.include_router(api_actions_text2img_stability_ai.router, tags=[f"{prefix}/text2img"])
# img2img
router.include_router(image_mixer_stable_diffusion.router, tags=[f"{prefix}/img2img"])
# text2video
router.include_router(api_actions_text2video_stable_diffusion.router, tags=[f"{prefix}/text2video"])
# text2audio
router.include_router(api_actions_text2audio_speech_openai.router, tags=[f"{prefix}/text2audio"])
# audio2text
router.include_router(api_actions_audio2text_transcription_openai.router, tags=[f"{prefix}/audio2text"])
router.include_router(api_actions_audio2text_translation_openai.router, tags=[f"{prefix}/audio2text"])
