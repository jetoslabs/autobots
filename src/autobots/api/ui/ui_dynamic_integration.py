from fastapi import APIRouter, Depends, Request
from gotrue import UserResponse

from src.autobots import SettingsProvider
from src.autobots.api.deps import get_user_from_cookie
from src.autobots.api.ui import templates

router = APIRouter()


@router.get("/dynamic_integration")
async def page_dynamic_integration(request: Request, user: UserResponse | None = Depends(get_user_from_cookie)):
    if not user:
        return templates.TemplateResponse("index.html", {"request": request})

    settings = SettingsProvider.sget()
    if user:
        return templates.TemplateResponse("dynamic_integration.html",
                                          {"request": request, "user": user.user, "version": settings.VERSION})


@router.get("/dynamic_integration/quote")
async def dynamic_integration_title(request: Request, user: UserResponse | None = Depends(get_user_from_cookie)):
    if not user:
        return "Not Authorized"

    return "Dynamic Integration"
