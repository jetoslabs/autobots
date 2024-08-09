from fastapi import APIRouter

from src.autobots.api.v1 import api_agents, api_action_type, api_docs, api_openai_storage
from src.autobots.api.v1.api_action_graph import api_action_graphs
from src.autobots.api.v1.api_action_graph_result import api_action_graph_results
from src.autobots.api.v1.api_action_result import api_action_results
from src.autobots.api.v1.api_action_chat import api_action_chat
from src.autobots.api.v1.api_action_market import api_actions_market
from src.autobots.api.v1.api_action_type.stable_diffusion import fetch_stable_diffusion
from src.autobots.api.v1.api_action import api_action
from src.autobots.api.v1.api_auth import api_auth
from src.autobots.api.v1.api_auth_secrets import api_secrets
from src.autobots.api.v1.api_datastore import api_datastore
from src.autobots.api.v1.api_vectorstore import api_vectorstore
from src.autobots.api.v1.api_files import api_files
from src.autobots.api.v1.api_hello import api_hello
from src.autobots.api.v1.api_schedules import api_schedules
from src.autobots.api.v1.api_poll_graph import api_poll_graph
from src.autobots.core.settings import SettingsProvider

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
router.include_router(api_action_graph_results.router)
router.include_router(api_schedules.router)
router.include_router(api_files.router)
router.include_router(api_datastore.router)
router.include_router(api_vectorstore.router)
router.include_router(api_openai_storage.router)
router.include_router(api_agents.router)
router.include_router(api_secrets.router)
router.include_router(api_poll_graph.router)
# api docs router
router_docs = APIRouter(prefix=SettingsProvider.sget().API_v1)

router.include_router(api_docs.router, prefix="", tags=["docs"])
