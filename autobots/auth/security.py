import gotrue
from fastapi import HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyQuery, APIKeyHeader, APIKeyCookie
from gotrue.errors import AuthApiError
from jose import jwt
from starlette.status import HTTP_403_FORBIDDEN

from autobots.auth.data_models import JwtPayload
from autobots.conn.supabase.supabase import get_supabase
from autobots.core.log import log
from autobots.core.settings import SettingsProvider


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{SettingsProvider.sget().API_v1}{SettingsProvider.sget().API_AUTH}{SettingsProvider.sget().API_AUTH_TOKEN}",
    scheme_name="JWT"
)


def decode_access_token(token: str, audience: str = "authenticated") -> JwtPayload | None:
    settings = SettingsProvider.sget()
    try:
        # Decoding token independently
        decoded_jwt: dict = jwt.decode(
            token=token,
            key=settings.JWT_SECRET_KEY,
            algorithms=settings.JWT_ALGORITHM,
            options=None,
            audience=audience,
            issuer=None,
            subject=None,
            access_token=None
        )
        token_payload: JwtPayload = JwtPayload(**decoded_jwt)
        # log.debug(token_payload)
        return token_payload
    except Exception as e:
        log.exception(e)


def supabase_decode_access_token(token: str, audience: str = None) -> gotrue.UserResponse:
    """
    Decodes token
    :param token:
    :param audience:
    :return:
    """
    try:
        # Decoding token using supabase to get user
        user_res: gotrue.UserResponse = get_supabase().client.auth.get_user(token)
        if not user_res.user.email:
            raise HTTPException(403, "Could not validate credentials")
        return user_res

    except AuthApiError | Exception as e:
        log.exception(e)
        raise e


def get_user_from_creds(token: str = Depends(oauth2_scheme)) -> gotrue.UserResponse:
    """
    Decodes token and returns User info
    :param token:
    :return:
    """
    try:
        jwt_payload: gotrue.UserResponse = supabase_decode_access_token(token, audience="authenticated")
        if not jwt_payload.user.email:
            raise HTTPException(403, "Could not validate credentials")
        return jwt_payload
    except Exception as e:
        log.exception(e)


api_key_query = APIKeyQuery(name="Authorization", auto_error=False)
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
api_key_cookie = APIKeyCookie(name="Authorization", auto_error=False)


def get_user_from_access_token(
        api_key_query: str = Security(api_key_query),
        api_key_header: str = Security(api_key_header),
        api_key_cookie: str = Security(api_key_cookie),
) -> gotrue.UserResponse:
    try:
        if api_key_query:
            return supabase_decode_access_token(api_key_query.split(" ")[1], audience="authenticated")
        elif api_key_header:
            return supabase_decode_access_token(api_key_header.split(" ")[1], audience="authenticated")
        elif api_key_cookie:
            return supabase_decode_access_token(api_key_cookie.split(" ")[1], audience="authenticated")

    except Exception as e:
        log.exception(e)

    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )
