from typing import Dict, Literal

from src.autobots.conn.zoho.zoho import Zoho
from src.autobots.conn.zoho.zoho_model import ZohoTokenRefreshRequest
from src.autobots.data_model.context import Context
from src.autobots.secret.app_auth.app_auth_abc import AppAuthABC
from src.autobots.secret.app_auth.app_auth_model import AppAuthSecret, AuthData


class ZohoAppAuthMeta(ZohoTokenRefreshRequest):
    pass


class ZohoAppAuth(AppAuthSecret):
    app: str = "zoho"
    api_domain: Literal[
        "https://www.zohoapis.ca",
        "https://www.zohoapis.eu",
        "https://www.zohoapis.com.cn",
        "https://www.zohoapis.com",
        "https://www.zohoapis.com.au",
        "https://www.zohoapis.in",
        "https://www.zohoapis.jp"
    ] = "https://www.zohoapis.com"
    auth_meta: ZohoAppAuthMeta | None = None


class ZohoAuth(AppAuthABC):

    @staticmethod
    def get_auth_data_type():
        return ZohoAppAuth

    @staticmethod
    async def update_auth_header(ctx: Context, auth: ZohoAppAuth) -> ZohoAppAuth:
        header = await ZohoAuth.create_auth_header(auth.auth_meta)
        return ZohoAppAuth(
            app=auth.app,
            auth_meta=auth.auth_meta,
            auth_data=AuthData(header=header)
        )

    @staticmethod
    async def create_auth_header(req: ZohoAppAuthMeta) -> Dict[str, str]:
        header = {}
        if req.api_domain and req.client_id and req.client_secret and req.refresh_token:
            api_req = ZohoTokenRefreshRequest(**req.model_dump(exclude_none=True))
            res = await Zoho.refresh_token(api_req)
            header = {"Authorization": f"Zoho-oauthtoken {res.access_token}"}
        return header
