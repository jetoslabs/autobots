from pydantic import BaseModel, Field

from src.autobots.conn.only_auth.zendesk.zendesk import Zendesk
from src.autobots.data_model.context import Context
from src.autobots.secret.app_auth.app_auth_abc import AppAuthABC
from src.autobots.secret.app_auth.app_auth_model import AppAuthSecret, AuthData
from src.autobots.secret.app_auth.app_auths_enum import APP_AUTHS


class ZendeskAppAuthMeta(BaseModel):
    api_key: str | None = Field(...)


class ZendeskAppAuth(AppAuthSecret):
    app: str = "zendesk"
    api_domain: str
    auth_meta: ZendeskAppAuthMeta | None = None


class ZendeskAuth(AppAuthABC):

    @staticmethod
    def get_auth_data_type():
        return ZendeskAppAuth

    @staticmethod
    async def update_auth_header(ctx: Context, auth: ZendeskAppAuth) -> ZendeskAppAuth:
        assert auth.app == APP_AUTHS.zendesk.value
        header = await Zendesk.create_auth_header(auth.auth_meta.api_key)
        return ZendeskAppAuth(
            app=auth.app,
            auth_meta=auth.auth_meta,
            auth_data=AuthData(header=header)
        )
