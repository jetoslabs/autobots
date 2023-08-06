import gotrue
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from gotrue import AuthResponse

from autobots.auth.auth import get_auth
from autobots.auth.data_models import BearerAccessToken
from autobots.auth.security import get_user_from_access_token, get_user_from_creds
from autobots.core.settings import get_settings

router = APIRouter()


@router.post("/")
def return_user_and_session(form_data: OAuth2PasswordRequestForm = Depends()) -> AuthResponse:
    """
    Returns Auth Response (User and Session)
    :return: AuthResponse
    """

    auth_res: AuthResponse = get_auth().sign_in_with_password(
        form_data.username, form_data.password
    )

    return auth_res


@router.post(get_settings().API_AUTH_TOKEN)
def return_token(form_data: OAuth2PasswordRequestForm = Depends()) -> BearerAccessToken:
    """
    OAuth2 endpoint
    signs in user(username/password) and returns JWT token
    :return: BearerToken
    """

    auth_res: AuthResponse = get_auth().sign_in_with_password(
        form_data.username, form_data.password
    )

    bearer_token: BearerAccessToken = BearerAccessToken(
        access_token=auth_res.session.access_token,
        token_type="Bearer"
    )

    return bearer_token


@router.post(f"/test/token")
def test_auth_access_token(user_res: gotrue.UserResponse = Depends(get_user_from_access_token)) -> gotrue.User:
    return user_res.user


@router.post("/test/creds")
def test_auth_creds(user_res: gotrue.UserResponse = Depends(get_user_from_creds)) -> gotrue.User:
    return user_res.user
