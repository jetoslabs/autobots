from fastapi import HTTPException
from pydantic import BaseModel

from src.autobots.exception.app_exception import AppException
from src.autobots.secret.app_auth.app_auth_model import AppAuthSecret
from src.autobots.secret.app_auth.app_auth_type.slack_auth import SlackAuth
from src.autobots.secret.app_auth.app_auth_type.zoho_auth import ZohoAuth
from src.autobots.secret.app_auth.app_auths_enum import APP_AUTHS

from src.autobots.data_model.context import Context


class AppAuthFactory:

    @staticmethod
    async def get_data_type(ctx, app: str) -> BaseModel:
        match app:
            case APP_AUTHS.slack.value:
                data_type = SlackAuth.get_auth_data_type()
                return data_type
            case APP_AUTHS.zoho.value:
                data_type = ZohoAuth.get_auth_data_type()
                return data_type
            case _:
                raise HTTPException(status_code=404, detail="App not found")

    @staticmethod
    async def update_auth_header(ctx: Context, app_auth: AppAuthSecret) -> AppAuthSecret | Exception:
        match app_auth.app:
            case APP_AUTHS.slack.value:
                slack_auth = SlackAuth.get_auth_data_type().model_validate(app_auth.model_dump(exclude_none=True))
                updated_slack_auth = await SlackAuth.update_auth_header(ctx, slack_auth)
                return AppAuthSecret(**updated_slack_auth.model_dump(exclude_none=True))
            case APP_AUTHS.zoho.value:
                zoho_auth = ZohoAuth.get_auth_data_type().model_validate(app_auth.model_dump(exclude_none=True))
                updated_zoho_auth = await ZohoAuth.update_auth_header(ctx, zoho_auth)
                return AppAuthSecret(**updated_zoho_auth.model_dump(exclude_none=True))
            case _:
                return AppException(detail="Cannot update auth header", http_status=501)
