from fastapi import APIRouter

from src.autobots.api.ui import ui_most

router = APIRouter()
router.include_router(ui_most.router)
