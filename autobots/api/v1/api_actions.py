from fastapi import APIRouter

from autobots.action.action_manager import ActionManager
from autobots.action.action_types import ActionType

router = APIRouter()


@router.get("/types")
async def get_action_types():
    return ActionManager.get_action_types()
