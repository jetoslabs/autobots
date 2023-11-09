from fastapi import APIRouter

from autobots.api.v1.api_actions import api_actions, api_action_create, api_actions_market
from autobots.api.v1.api_actions.stable_diffusion import fetch_stable_diffusion
from autobots.api.v1.api_actions.text2img import api_actions_text2img_stable_diffusion, api_actions_text2img_openai, api_actions_text2img_stability_ai
from autobots.api.v1.api_actions.img2img import image_mixer_stable_diffusion
from autobots.api.v1.api_actions.text2text import api_actions_text2text
from autobots.api.v1.api_actions.text2video import api_actions_text2video_stable_diffusion

router = APIRouter()

router.include_router(api_actions.router, tags=["actions"])
# router.include_router(api_action_create.router)
# text2text
router.include_router(api_actions_text2text.router, tags=["actions/text2text"])
# text2img
router.include_router(api_actions_text2img_openai.router, tags=["actions/text2img"])
router.include_router(api_actions_text2img_stable_diffusion.router, tags=["actions/text2img"])
router.include_router(api_actions_text2img_stability_ai.router, tags=["actions/text2img"])
# img2img
router.include_router(image_mixer_stable_diffusion.router, tags=["actions/img2img"])
# text2video
router.include_router(api_actions_text2video_stable_diffusion.router, tags=["actions/text2video"])
