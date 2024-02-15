from fastapi import APIRouter

from src.autobots import SettingsProvider
from src.autobots.api.v1.api_agents import api_agents

router = APIRouter(
    prefix=SettingsProvider.sget().API_AGENTS, tags=[SettingsProvider.sget().API_AGENTS]
)

router.include_router(api_agents.router)
