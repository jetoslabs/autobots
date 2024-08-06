import gotrue
from fastapi import APIRouter, Depends
from starlette.requests import Request

from src.autobots import SettingsProvider
from src.autobots.auth.security import get_user_from_access_token

router = APIRouter(prefix=SettingsProvider.sget().API_AUTH, tags=[SettingsProvider.sget().API_AUTH])


# https://developers.google.com/identity/protocols/oauth2/web-server#httprest
@router.get("/google/oauth-callback")
async def google_callback(
        request: Request,
        code: str | None = None,
        error: str | None = None,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
):


    return {
        "code": code,
        "error": error,
    }
