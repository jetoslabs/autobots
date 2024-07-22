from pydantic import BaseModel, Field

from src.autobots.conn.slack.slack import Slack
from src.autobots.data_model.context import Context
from src.autobots.secret.app_auth.app_auth_abc import AppAuthABC
from src.autobots.secret.app_auth.app_auth_model import AppAuthSecret, AuthData
from src.autobots.secret.app_auth.app_auths_enum import APP_AUTHS


class SlackAppAuthMeta(BaseModel):
    api_key: str | None = Field(..., alias='api_key')


class SlackAppAuth(AppAuthSecret):
    app: str = "slack"
    api_domain: str = "https://slack.com"
    auth_meta: SlackAppAuthMeta | None = None


class SlackAuth(AppAuthABC):

    @staticmethod
    def get_auth_data_type():
        return SlackAppAuth

    @staticmethod
    async def update_auth_header(ctx: Context, auth: SlackAppAuth) -> SlackAppAuth:
        assert auth.app == APP_AUTHS.slack.value
        header = await Slack.create_auth_header(auth.auth_meta.api_key)
        return SlackAppAuth(
            app=auth.app,
            auth_meta=auth.auth_meta,
            auth_data=AuthData(header=header)
        )
