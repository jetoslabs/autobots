from fastapi import APIRouter
from src.autobots.api.ui import ui_most, ui_dynamic_integration

router = APIRouter()
router.include_router(ui_most.router)
router.include_router(ui_dynamic_integration.router)
