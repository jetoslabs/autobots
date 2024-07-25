from fastapi import HTTPException
from loguru import logger
from pydantic import BaseModel

from src.autobots.exception.app_exception import AppException
from src.autobots.secret.app_auth.app_auth_map import APP_AUTH_MAP
from src.autobots.secret.app_auth.app_auth_model import AppAuthSecret
from src.autobots.secret.app_auth.app_auths_enum import APP_AUTHS

from src.autobots.data_model.context import Context


class AppAuthFactory:

    @staticmethod
    async def get_data_type(ctx, app: APP_AUTHS) -> BaseModel:
        try:
            app_auth_name = app.value
            app_auth = APP_AUTH_MAP.get(app_auth_name)
            data_type = app_auth.get_auth_data_type()
            return data_type
        except Exception:
            logger.bind(ctx=ctx).info("App not found")
            raise HTTPException(status_code=404, detail="App not found")

    @staticmethod
    async def update_auth_header(ctx: Context, app_auth: AppAuthSecret) -> AppAuthSecret | Exception:
        try:
            app_auth_name = app_auth.app
            app_auth_type = APP_AUTH_MAP.get(app_auth_name)
            auth = app_auth_type.get_auth_data_type().model_validate(app_auth.model_dump(exclude_none=True))
            updated_auth = await app_auth_type.update_auth_header(ctx, auth)
            return AppAuthSecret(**updated_auth.model_dump(exclude_none=True))
        except Exception as e:
            logger.bind(ctx=ctx, e=str(e)).info(f"Cannot update auth header, err: {str(e)}")
            return AppException(detail="Cannot update auth header", http_status=501)
