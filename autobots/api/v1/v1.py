from fastapi import APIRouter

from autobots.api.v1 import api_docs, api_agents, api_action_type
from autobots.api.v1.api_action_graph import api_action_graphs
from autobots.api.v1.api_action_result import api_action_results
from autobots.api.v1.api_action_chat import api_action_chat
from autobots.api.v1.api_action_market import api_actions_market
from autobots.api.v1.api_action_type.stable_diffusion import fetch_stable_diffusion
from autobots.api.v1.api_action import api_action
from autobots.api.v1.api_auth import api_auth
from autobots.api.v1.api_datastore import api_datastore
from autobots.api.v1.api_hello import api_hello
from autobots.core.settings import SettingsProvider

# API v1 router
router = APIRouter(prefix=SettingsProvider.sget().API_v1)

router.include_router(api_hello.router)
router.include_router(api_auth.router)
router.include_router(api_action.router)
router.include_router(api_action_type.router)
router.include_router(api_action_results.router)
router.include_router(fetch_stable_diffusion.router)
router.include_router(api_action_chat.router)
router.include_router(api_actions_market.router)
router.include_router(api_action_graphs.router)
router.include_router(api_datastore.router)
router.include_router(api_agents.router)

# api docs router
router_docs = APIRouter(prefix=SettingsProvider.sget().API_v1)

router.include_router(api_docs.router, prefix="", tags=["docs"])
