from typing import Literal

import httpx
from fastapi import HTTPException
from pydantic import BaseModel
from retry import retry

from src.autobots.data_model.context import Context


class GoogleAuthorizationCodeRq(BaseModel):
    client_id: str
    redirect_uri: str
    response_type: str = "code"
    scope: str
    access_type: str = "offline"


class GoogleAuthorizationCode(BaseModel):
    code: str | None = None
    error: str | None = None


class GoogleRefreshTokenRq(BaseModel):
    client_id: str
    client_secret: str
    grant_type: Literal["authorization_code"] = "authorization_code"
    redirect_uri: str


class GoogleAccessTokenRq(GoogleRefreshTokenRq):
    code: str


class GoogleRefreshedAccessToken(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    scope: str


class GoogleAccessToken(GoogleRefreshedAccessToken):
    refresh_token: str


class Google:
    AUTHORIZATION_CODE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    REFRESH_TOKEN_URL = "https://oauth2.googleapis.com/token"

    @staticmethod
    @retry(exceptions=Exception, tries=3, delay=5, backoff=2)
    async def oauth_token_flow(ctx: Context, rq: GoogleAuthorizationCodeRq) -> GoogleAccessToken | Exception:
        auth_code = await Google.authorization_code(ctx=ctx, rq=rq)
        match auth_code:
            case Exception():
                return auth_code

        token_rq = GoogleAccessTokenRq(
            client_id=rq.client_id,
            client_secret=rq.client_secret,
            code=auth_code.code,
            grant_type="authorization_code",
            redirect_uri=rq.redirect_uri,
        )
        token_rs = await Google.access_token(ctx=ctx, rq=token_rq)
        return token_rs

    @staticmethod
    @retry(exceptions=Exception, tries=3, delay=5, backoff=2)
    async def authorization_code(ctx: Context, rq: GoogleAuthorizationCodeRq) -> GoogleAuthorizationCode | Exception:
        async with httpx.AsyncClient() as client:
            res = await client.post(str(Google.AUTHORIZATION_CODE_URL), params=rq.model_dump(exclude_none=True))
            if res.status_code == 200:
                return GoogleAuthorizationCode(**res.json())
            else:
                return HTTPException(status_code=res.status_code, detail=res.text)

    @staticmethod
    @retry(exceptions=Exception, tries=3, delay=5, backoff=2)
    async def access_token(ctx: Context, rq: GoogleAccessTokenRq) -> GoogleAccessToken | Exception:
        async with httpx.AsyncClient() as client:
            res = await client.post(str(Google.TOKEN_URL), params=rq.model_dump(exclude_none=True))
            if res.status_code == 200:
                return GoogleAccessToken(**res.json())
            else:
                return HTTPException(status_code=res.status_code, detail=res.text)

    @staticmethod
    @retry(exceptions=Exception, tries=3, delay=5, backoff=2)
    async def refresh_access_token(ctx: Context, rq: GoogleRefreshTokenRq) -> GoogleRefreshedAccessToken | Exception:
        async with httpx.AsyncClient() as client:
            res = await client.post(str(Google.TOKEN_URL), params=rq.model_dump(exclude_none=True))
            if res.status_code == 200:
                return GoogleRefreshedAccessToken(**res.json())
            else:
                return HTTPException(status_code=res.status_code, detail=res.text)
