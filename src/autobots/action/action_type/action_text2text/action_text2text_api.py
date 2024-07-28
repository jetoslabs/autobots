import json
import typing
from typing import Type

import httpx
from httpx._types import PrimitiveData
from loguru import logger
from pydantic import BaseModel, ConfigDict, HttpUrl

from src.autobots.action.action_type.abc.ActionABC import ActionABC
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.data_model.context import Context
from src.autobots.secret.app_auth.app_auth_model import AppAuthSecretFind, OptionalAppAuthSecret, AppAuthSecret
from src.autobots.secret.app_auth.app_auth_secret_crud import AppAuthSecretCRUD
from src.autobots.secret.app_auth.user_app_auth_secret_handler import UserAppAuthSecretHandler
from src.autobots.user.user_orm_model import UserORM


class APIRequest(BaseModel):
    method: str
    url: str
    # content: typing.Optional[str] = None
    # data: typing.Optional[typing.Mapping[str, typing.Any]] = None
    headers: typing.Optional[typing.Mapping[str, str]] = None
    params: typing.Optional[typing.Mapping[str, typing.Union[PrimitiveData]]] = None
    files: typing.Optional[typing.Mapping[str, bytes]] = None
    body: typing.Optional[typing.Dict[str, typing.Any]] = None
    # json: typing.Optional[str] = None
    # cookies: typing.Optional[typing.Dict[str, str]] = None
    # auth: typing.Union[typing.Tuple[typing.Union[str, bytes]]] = None
    follow_redirects: typing.Union[bool] = False
    timeout: typing.Optional[float] = None
    # extensions: typing.Optional[typing.MutableMapping[str, typing.Any]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class APIInput(APIRequest):
    method: typing.Optional[str] = None
    url: typing.Optional[str] = None


class APIResponse(BaseModel):
    status_code: int
    # headers: typing.Optional[typing.Mapping[str, str]] = None
    content: typing.Optional[str] = None
    # text: typing.Optional[str] = None
    # stream: typing.Union[SyncByteStream, AsyncByteStream, None] = None
    # request: typing.Optional[Request] = None
    # extensions: typing.Optional[typing.MutableMapping[str, typing.Any]] = None
    # history: typing.Optional[typing.List["Response"]] = None
    # default_encoding: str = "utf-8"

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ActionText2textAPI(
    ActionABC[APIRequest, APIRequest, APIRequest, APIInput, APIResponse]
):
    type = ActionType.text2text_api_call

    @staticmethod
    def get_description() -> str:
        return "Make an API call"

    @staticmethod
    def get_config_create_type() -> Type[APIRequest]:
        return APIRequest

    @staticmethod
    def get_config_update_type() -> Type[APIRequest]:
        return APIRequest

    @staticmethod
    def get_config_type() -> Type[APIRequest]:
        return APIRequest

    @staticmethod
    def get_input_type() -> Type[APIInput]:
        return APIInput

    @staticmethod
    def get_output_type() -> Type[APIResponse]:
        return APIResponse

    @staticmethod
    async def update_config(config: APIRequest, config_update: APIInput) -> APIRequest:
        config_dict = config.model_dump(exclude_none=True)
        config_update_dict = config_update.model_dump(exclude_none=True)
        updated_config_dict = config_dict | config_update_dict
        updated_config = APIRequest.model_validate(updated_config_dict)
        return updated_config

    def __init__(self, action_config: APIRequest, user: UserORM | None = None):
        super().__init__(action_config=action_config, user=user)

    async def run_action(self, ctx: Context, action_input: APIInput) -> APIResponse | Exception:
        try:
            config = await ActionText2textAPI.update_config(self.action_config, action_input)
            api_response = await self.run_or_err(ctx, config)
            return api_response
        except Exception as e:
            logger.error(str(e))
            return e

    async def run_tool(self, action_config: APIRequest, ctx: Context) -> APIResponse | Exception:
        try:
            config = await ActionText2textAPI.create_config(action_config)
            api_response = await self.run_or_err(ctx=ctx, action_config=config)
            return api_response
        except Exception as e:
            logger.error(str(e))
            return e

    async def run_or_err(self, ctx: Context, action_config: APIRequest) -> APIResponse:
        config = await self.build_headers(ctx, action_config)
        # From body to content field
        config_dict = config.model_dump(exclude_none=True)
        if config.body:
            config_dict.pop("body")  # removing
            config_dict["content"] = json.dumps(config.body)  # moving

        client = httpx.AsyncClient()
        resp = await client.request(**config_dict)
        api_response = APIResponse(
            status_code=resp.status_code,
            # headers=resp.headers,
            content=resp.content,
            # text=resp.text,
            # extensions=resp.extensions,
            # default_encoding=resp.default_encoding
        )
        logger.bind(ctx=ctx, api_request=config_dict, api_response=api_response).info("API called")
        return api_response

    async def build_headers(self, ctx: Context, config: APIRequest) -> APIRequest:
        content_type_header = await self.get_content_type_header_if_not_set(ctx, config)
        authorization_header = await self.get_authorization_header(ctx, config)
        config_dict = config.model_dump(exclude_none=True)
        config_dict["headers"] = config_dict["headers"] | authorization_header | content_type_header
        return APIRequest.model_validate(config_dict)

    async def get_authorization_header(self, ctx: Context, config: APIRequest) -> typing.Dict[str, str]:
        api_url = HttpUrl(config.url)
        api_domain = f"{api_url.scheme}://{api_url.host}"
        app_auth_find = AppAuthSecretFind(secret=OptionalAppAuthSecret(api_domain=api_domain))
        db = next(get_mongo_db())
        user_secret_doc = await UserAppAuthSecretHandler.read(
            ctx=ctx,
            user=self.user,
            crud=AppAuthSecretCRUD(db),
            app_auth_find=app_auth_find
        )
        if user_secret_doc:
            app_auth_secret = AppAuthSecret.model_validate(user_secret_doc.secret)
            headers = app_auth_secret.auth_data.header
            return headers
        else:
            logger.bind(ctx=ctx).error("No secret found")
            return {}

    async def get_content_type_header_if_not_set(self, ctx: Context, config: APIRequest, default: str = "application/json") -> typing.Dict[str, str]:
        # Content-type
        config_dict = config.model_dump(exclude_none=True)
        is_content_type_set = False
        for key in config_dict["headers"]:
            if isinstance(key, str):
                if "content-type" == key.lower():
                    is_content_type_set = True
                    break
        if not is_content_type_set:
            return {"Content-Type": default}
        return {}