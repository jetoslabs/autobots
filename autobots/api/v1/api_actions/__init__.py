from fastapi import APIRouter

from autobots.api.v1.api_actions import api_actions, api_action_create, api_actions_market
from autobots.api.v1.api_actions.stable_diffusion import fetch_stable_diffusion
from autobots.api.v1.api_actions.text2img import api_actions_text2img_stable_diffusion, api_actions_text2img_openai, api_actions_text2img_stability_ai
from autobots.api.v1.api_actions.img2img import image_mixer_stable_diffusion
from autobots.api.v1.api_actions.text2text import text2text
from autobots.api.v1.api_actions.text2video import api_actions_text2video_stable_diffusion

router = APIRouter()

router.include_router(api_actions.router)
# router.include_router(api_action_create.router)
# text2text
router.include_router(text2text.router)
# text2img
router.include_router(api_actions_text2img_openai.router)
router.include_router(api_actions_text2img_stable_diffusion.router)
router.include_router(api_actions_text2img_stability_ai.router)
# img2img
router.include_router(image_mixer_stable_diffusion.router)
# text2video
router.include_router(api_actions_text2video_stable_diffusion.router)
router.include_router(fetch_stable_diffusion.router)
