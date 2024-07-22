import httpx
from fastapi import HTTPException
from pydantic import HttpUrl
from retry import retry

from src.autobots.conn.only_auth.zoho.zoho_model import ZohoTokenGenerateResponse, ZohoTokenRefreshResponse, \
    ZohoTokenRefreshRequest, ZohoTokenGenerateRequest


class Zoho:
    TOKEN_PATH = "/oauth/v2/token"
    API_DOMAIN_TO_AUTH_API = {
        "https://www.zohoapis.ca": "https://accounts.zohocloud.ca",
        "https://www.zohoapis.eu": "https://accounts.zoho.eu",
        "https://www.zohoapis.com.cn": "https://accounts.zoho.com.cn",
        "https://www.zohoapis.com": "https://accounts.zoho.com",
        "https://www.zohoapis.com.au": "https://accounts.zoho.com.au",
        "https://www.zohoapis.in": "https://accounts.zoho.in",
        "https://www.zohoapis.jp": "https://accounts.zoho.jp",
    }

    @staticmethod
    @retry(exceptions=Exception, tries=3, delay=5, backoff=2)
    async def generate_token(req: ZohoTokenGenerateRequest) -> ZohoTokenGenerateResponse:
        """self client: https://www.zoho.com/accounts/protocol/oauth/self-client/authorization-code-flow.html"""

        # url = f"{req.api_domain}{Zoho.TOKEN_PATH}".replace("//", "/")
        url = Zoho.get_auth_url(req.api_domain)
        params = {
            "client_id": req.client_id,
            "client_secret": req.client_secret,
            "grant_type": "authorization_code",
            "code": req.auth_code,
        }
        async with httpx.AsyncClient() as client:
            res = await client.post(str(url), params=params)
            if res.status_code == 200:
                return ZohoTokenGenerateResponse(**res.json())
            else:
                raise HTTPException(status_code=res.status_code, detail=res.text)

    @staticmethod
    @retry(exceptions=Exception, tries=3, delay=5, backoff=2)
    async def refresh_token(req: ZohoTokenRefreshRequest) -> ZohoTokenRefreshResponse:
        url = await Zoho.get_auth_url(req.api_domain)
        params = {
            "client_id": req.client_id,
            "client_secret": req.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": req.refresh_token,
        }
        async with httpx.AsyncClient() as client:
            res = await client.post(str(url), params=params)
            if res.status_code == 200:
                return ZohoTokenRefreshResponse(**res.json())
            else:
                raise HTTPException(status_code=res.status_code, detail=res.text)

    @staticmethod
    async def get_auth_url(api_domain: str) -> HttpUrl:
        auth_api_host = Zoho.API_DOMAIN_TO_AUTH_API.get(api_domain, "")
        return HttpUrl(f"{auth_api_host}{Zoho.TOKEN_PATH}")
