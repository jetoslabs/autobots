from fastapi import APIRouter

from autobots.api.v1 import api_hello, api_auth, api_actions, api_action_graphs, api_docs, \
    api_datastore, api_chat, api_agents, api_action_results
from autobots.api.v1.api_actions import api_actions_market
from autobots.core.settings import SettingsProvider

settings = SettingsProvider.sget()
router = APIRouter(prefix=settings.API_v1)
router.include_router(api_hello.router, prefix=settings.API_Hello, tags=["hello"])
router.include_router(api_auth.router, prefix=settings.API_AUTH, tags=["auth"])
router.include_router(api_actions.router, prefix=settings.API_ACTIONS, tags=["actions"])
router.include_router(api_actions_market.router, prefix=settings.API_ACTIONS, tags=["actions_market"])
router.include_router(api_action_results.router, prefix=settings.API_ACTION_RESULTS, tags=["action_results"])
router.include_router(api_action_graphs.router, prefix=settings.API_ACTION_GRAPHS, tags=["action_graphs"])
router.include_router(api_datastore.router, prefix=settings.API_DATASTORE, tags=["datastore"])
router.include_router(api_chat.router, prefix=settings.API_CHAT, tags=["chat"])
router.include_router(api_agents.router, prefix=settings.API_AGENTS, tags=["agents"])

router_docs = APIRouter(prefix=settings.API_v1)
router.include_router(api_docs.router, prefix="", tags=["docs"])
