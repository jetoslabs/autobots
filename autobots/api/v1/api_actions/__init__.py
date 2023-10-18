from fastapi import APIRouter

from autobots.api.v1.api_actions import api_actions, api_action_create
from autobots.api.v1.api_actions.text2img import text2img_stable_diffusion
from autobots.api.v1.api_actions.img2img import image_mixer_stable_diiffusion
from autobots.api.v1.api_actions.text2video import text2video_stable_diffusion

router = APIRouter()

router.include_router(api_actions.router)
router.include_router(api_action_create.router)
router.include_router(image_mixer_stable_diiffusion.router)
router.include_router(text2img_stable_diffusion.router)
router.include_router(text2video_stable_diffusion.router)
