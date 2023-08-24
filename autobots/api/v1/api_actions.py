from fastapi import APIRouter

from autobots.action.action_types import ActionType

router = APIRouter()


@router.get("/types")
async def get_action_types():
    action_types = [action_type for action_type in ActionType]
    return action_types
