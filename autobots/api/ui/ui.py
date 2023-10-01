from fastapi import APIRouter

from autobots.api.ui import ui_most, ui_llm_action

router = APIRouter()
router.include_router(ui_most.router)
router.include_router(ui_llm_action.router)

