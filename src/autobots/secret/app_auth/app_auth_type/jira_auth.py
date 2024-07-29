from pydantic import BaseModel, Field

from src.autobots.conn.only_auth.jira.jira import Jira
from src.autobots.data_model.context import Context
from src.autobots.secret.app_auth.app_auth_abc import AppAuthABC
from src.autobots.secret.app_auth.app_auth_model import AppAuthSecret, AuthData
from src.autobots.secret.app_auth.app_auths_enum import APP_AUTHS


class JiraAppAuthMeta(BaseModel):
    api_key: str | None = Field(..., alias='api_key')


class JiraAppAuth(AppAuthSecret):
    app: str = "jira"
    api_domain: str
    auth_meta: JiraAppAuthMeta | None = None


class JiraAuth(AppAuthABC):

    @staticmethod
    def get_auth_data_type():
        return JiraAppAuth

    @staticmethod
    async def update_auth_header(ctx: Context, auth: JiraAppAuth) -> JiraAppAuth:
        assert auth.app == APP_AUTHS.jira.value
        header = await Jira.create_auth_header(auth.auth_meta.api_key)
        return JiraAppAuth(
            app=auth.app,
            auth_meta=auth.auth_meta,
            auth_data=AuthData(header=header)
        )
