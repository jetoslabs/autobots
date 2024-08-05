from typing import List

from pydantic import BaseModel, ConfigDict, Field

from src.autobots.data_model.created_at import CreatedAt
from src.autobots.data_model.updated_at import UpdatedAt
from src.autobots.data_model.user_id import UserId
from src.autobots.secret.app_creds.apps_enum import APPS_ENUM


class ID(BaseModel):
    id: str = Field(..., alias='_id')


class OAuthCredsModel(BaseModel):
    client_id: str
    client_secret: str
    api_key: str
    scope: str


class ApiKeyCredsModel(BaseModel):
    api_key: str


class AppCredsCreate(BaseModel):
    app_name: APPS_ENUM.value
    creds: OAuthCredsModel | ApiKeyCredsModel


class AppCredsDocCreate(UserId, AppCredsCreate):
    pass


class AppCredsRead(ID):
    id: str | None = None
    app_name: APPS_ENUM.value | None = None


class AppCredsDocRead(UserId, AppCredsRead):
    pass


class AppCredsUpdate(ID, AppCredsCreate):
    app_name: APPS_ENUM.value | None = None
    creds: OAuthCredsModel | ApiKeyCredsModel | None = None


class AppCredsDocUpdate(UserId, AppCredsUpdate):
    pass


class AppCredsDeleteDoc(AppCredsDocRead):
    pass


class AppCredsLiteDoc(ID, CreatedAt, UpdatedAt, AppCredsDocRead):
    pass


class AppCredsLiteDocPage(BaseModel):
    docs: List[AppCredsLiteDoc]
    total_count: int
    limit: int
    offset: int


class AppCredsDoc(ID, CreatedAt, UpdatedAt, AppCredsDocCreate):
    __collection__ = "AppCreds"

    model_config = ConfigDict(populate_by_name=True)
