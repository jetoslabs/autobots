from typing import List

from pydantic import BaseModel, ConfigDict, Field

from src.autobots.core.database.crud import DocFindPage
from src.autobots.data_model.created_at import CreatedAt
from src.autobots.data_model.updated_at import UpdatedAt
from src.autobots.data_model.user_id import UserId
from src.autobots.secret.app_types import AppTypes


class ID(BaseModel):
    id: str = Field(..., alias="_id")


class OAuthCredsModel(BaseModel):
    client_id: str
    client_secret: str
    api_key: str
    scope: str


class ApiKeyCredsModel(BaseModel):
    api_key: str


class AppCredsCreate(BaseModel):
    app_name: str | AppTypes
    creds: OAuthCredsModel | ApiKeyCredsModel


class AppCredsDocCreate(UserId, AppCredsCreate):
    pass


class AppCredsRead(ID):
    id: str | None = None
    app_name: AppTypes | None = None


class AppCredsDocRead(UserId, AppCredsRead):
    pass


class AppCredsUpdate(AppCredsCreate):
    app_name: AppTypes | None = None
    creds: OAuthCredsModel | ApiKeyCredsModel | None = None


class AppCredsDocUpdate(ID, UserId, AppCredsUpdate):
    id: str


class AppCredsDeleteDoc(AppCredsDocRead):
    pass


class AppCredsLiteDoc(ID, UserId, CreatedAt, UpdatedAt):
    app_name: AppTypes
    model_config = ConfigDict(populate_by_name=True)


class AppCredsLiteDocPage(DocFindPage):
    docs: List[AppCredsLiteDoc]


class AppCredsDoc(ID, CreatedAt, UpdatedAt, AppCredsDocCreate):
    __collection__ = "AppCreds"

    model_config = ConfigDict(populate_by_name=True)
