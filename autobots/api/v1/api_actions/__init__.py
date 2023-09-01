from fastapi import APIRouter

from autobots.api.v1.api_actions import api_actions, api_action_create

router = APIRouter()

router.include_router(api_actions.router)
router.include_router(api_action_create.router)
