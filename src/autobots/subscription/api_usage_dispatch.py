from typing import Optional

from pydantic import EmailStr, BaseModel, HttpUrl
from requests import Request

from src.autobots.auth.data_models import JwtPayload
from src.autobots.auth.security import decode_access_token
from src.autobots.core.logging.log import Log


class Usage(BaseModel):
    user_id: str
    email: EmailStr
    url: HttpUrl


async def usage_info_dispatch(request: Request, call_next):
    jwt_payload = await get_jwt_payload(request)
    if jwt_payload:
        usage = Usage(
            user_id=jwt_payload.sub,
            email=jwt_payload.email,
            url=str(request.url)
        )
        Log.bind(**usage.model_dump()).debug("API usage")
    response = await call_next(request)
    return response


async def get_jwt_payload(request: Request) -> Optional[JwtPayload]:
    jwt_payload = None
    try:
        token = None
        if request and "Authorization" in dict(request.headers).keys():
            access_token = str(request.headers["Authorization"])
            token = access_token.split(" ")[1].removesuffix("\"")
        elif request and "cookie" in dict(request.headers).keys():
            access_token = str(request.headers["cookie"])
            token = access_token.split(" ")[1].removesuffix("\"")
        if token:
            jwt_payload = decode_access_token(token)
        return jwt_payload
    except Exception as e:
        Log.error(f"Error while get_jwt_payload: {e}")

