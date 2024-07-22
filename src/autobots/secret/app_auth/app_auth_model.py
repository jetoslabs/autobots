from enum import Enum
from typing import Dict, Any

from fastapi import HTTPException
from pydantic import BaseModel, field_validator
from starlette import status

from src.autobots.data_model.created_at import CreatedAt
from src.autobots.data_model.updated_at import UpdatedAt
from src.autobots.secret.app_auth.app_auths_enum import APP_AUTHS


class AuthData(BaseModel):
    header: Dict[str, str] = {}


class AppAuthSecret(BaseModel):
    app: str
    api_domain: str
    auth_meta: Dict[str, Any] | None = None
    auth_data: AuthData | None = None

    @classmethod
    @field_validator("app")
    def validate_app(cls, value):
        if isinstance(value, Enum):
            if value == "app":
                if not APP_AUTHS.__contains__(value):
                    assert APP_AUTHS.__contains__(value)
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return None


class OptionalAppAuthSecret(AppAuthSecret):
    app: str | None = None
    api_domain: str | None = None


class AppAuthSecretCreate(BaseModel):
    secret: AppAuthSecret


class UserAppAuthSecretDocCreate(AppAuthSecretCreate, CreatedAt, UpdatedAt):
    user_id: str


class AppAuthSecretUpdate(BaseModel):
    secret: OptionalAppAuthSecret | None = None


class UserAppAuthSecretDocUpdate(AppAuthSecretUpdate, UpdatedAt):
    id: str
    user_id: str


class AppAuthSecretFind(BaseModel):
    id: str | None = None
    secret: OptionalAppAuthSecret | None = None


class UserAppAuthSecretDocFind(AppAuthSecretFind):
    user_id: str
