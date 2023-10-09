from fastapi import APIRouter

from autobots.api.v1.api_agents import api_agents

router = APIRouter()

router.include_router(api_agents.router)
