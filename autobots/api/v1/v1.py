from fastapi import APIRouter

from autobots.api.v1 import api_hello, api_auth, api_prompts, api_graphs, api_actions, api_action_graphs
from autobots.core.settings import get_settings

router = APIRouter(prefix=get_settings().API_v1)

router.include_router(api_hello.router, prefix=get_settings().API_Hello, tags=["hello"])
router.include_router(api_auth.router, prefix=get_settings().API_AUTH, tags=["auth"])
router.include_router(api_actions.router, prefix=get_settings().API_ACTIONS, tags=["actions"])
router.include_router(api_action_graphs.router, prefix=get_settings().API_ACTION_GRAPHS, tags=["action_graphs"])
router.include_router(api_prompts.router, prefix=get_settings().API_PROMPTS, tags=["prompts"])
# router.include_router(api_graphs.router, prefix=get_settings().API_GRAPHS, tags=["graphs"])
