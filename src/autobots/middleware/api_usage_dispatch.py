from typing import Optional

from loguru import logger
from pydantic import EmailStr, BaseModel, HttpUrl
from fastapi import Request

from src.autobots.auth.data_models import JwtPayload
from src.autobots.auth.security import decode_access_token
from src.autobots.data_model.context import Context


class UsageStart(BaseModel):
    user_id: str
    email: EmailStr
    url: HttpUrl


class Usage(BaseModel):
    user_id: str | None = None
    email: EmailStr | None = None
    url: HttpUrl | None = None
    status_code: int | None = None


async def usage_info_dispatch(request: Request, call_next):
    ctx = request.state.context
    jwt_payload = await get_jwt_payload(ctx=ctx, request=request)
    if jwt_payload:
        ctx.user_id = jwt_payload.sub
    usage = Usage(
        user_id=jwt_payload.sub if jwt_payload else None,
        email=jwt_payload.email if jwt_payload else None,
        url=str(request.url),
    )
    logger.bind(ctx=ctx, **usage.model_dump()).debug("API use start")
    response = await call_next(request)
    usage = Usage(
        user_id=jwt_payload.sub if jwt_payload else None,
        email=jwt_payload.email if jwt_payload else None,
        url=str(request.url),
        status_code=response.status_code,
    )
    logger.bind(ctx=ctx, **usage.model_dump()).debug("API use complete")

    return response


async def get_jwt_payload(ctx: Context, request: Request) -> Optional[JwtPayload]:
    jwt_payload = None
    try:
        token = None
        if request and "authorization" in dict(request.headers).keys():
            access_token = str(request.headers["authorization"])
            if access_token:
                token = access_token.split(" ")[1].removesuffix("\"")
        elif request and "cookie" in dict(request.headers).keys():
            access_token = str(request.headers["cookie"])
            if access_token:
                token = access_token.split(" ")[1].removesuffix("\"")
        if token:
            jwt_payload = decode_access_token(token)
        return jwt_payload
    except Exception as e:
        logger.bind(ctx=ctx).error(f"Error while get_jwt_payload: {str(e)}")
