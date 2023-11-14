from typing import Optional

import gotrue
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from gotrue import AuthResponse
from pydantic import EmailStr, HttpUrl

from autobots.auth.auth import get_auth
from autobots.auth.data_models import BearerAccessToken
from autobots.auth.security import get_user_from_access_token, get_user_from_creds
from autobots.core.settings import SettingsProvider

router = APIRouter(prefix=SettingsProvider.sget().API_AUTH, tags=[SettingsProvider.sget().API_AUTH])


@router.post("/")
async def return_user_and_session(form_data: OAuth2PasswordRequestForm = Depends()) -> AuthResponse:
    """
    Returns Auth Response (User and Session)
    :return: AuthResponse
    """

    auth_res: AuthResponse = await get_auth().sign_in_with_password(
        form_data.username, form_data.password
    )

    return auth_res


@router.post(SettingsProvider.sget().API_AUTH_TOKEN)
async def return_token(form_data: OAuth2PasswordRequestForm = Depends()) -> BearerAccessToken:
    """
    OAuth2 endpoint
    signs in user(username/password) and returns JWT token
    :return: BearerToken
    """

    auth_res: AuthResponse = await get_auth().sign_in_with_password(
        form_data.username, form_data.password
    )

    bearer_token: BearerAccessToken = BearerAccessToken(
        access_token=auth_res.session.access_token,
        token_type="Bearer"
    )

    return bearer_token


@router.post(f"/token/test")
async def test_auth_access_token(user_res: gotrue.UserResponse = Depends(get_user_from_access_token)) -> gotrue.User:
    return user_res.user


@router.post("/creds/test")
async def test_auth_creds(user_res: gotrue.UserResponse = Depends(get_user_from_creds)) -> gotrue.User:
    return user_res.user


@router.post("/password/reset")
async def reset_password_email(email: EmailStr, redirect_to: Optional[HttpUrl] = None) -> bool:
    return await get_auth().reset_password_email(email, redirect_to)


@router.post("/session/refresh")
async def reset_password_email(refresh_token: str, user_res: gotrue.UserResponse = Depends(get_user_from_access_token)) -> AuthResponse:
    return await get_auth().refresh_session(refresh_token)
