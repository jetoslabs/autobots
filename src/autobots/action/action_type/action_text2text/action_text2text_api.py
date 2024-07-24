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

    # def __init__(self, action_config: APIRequest):
    #     super().__init__(action_config)

    async def run_action(self, action_input: APIInput) -> APIResponse | Exception:
        try:
            config = await ActionText2textAPI.update_config(self.action_config, action_input)
            config_dict = config.model_dump(exclude_none=True)

            if config.body:
                config_dict.pop("body")
                config_dict["content"] = json.dumps(config.body)
                config_dict["headers"]["Content-Type"] = "application/json"

            client = httpx.AsyncClient()
            # resp = await client.request(**config.model_dump(exclude_none=True))
            resp = await client.request(**config_dict)
            api_response = APIResponse(
                status_code=resp.status_code,
                # headers=resp.headers,
                content=resp.content,
                # text=resp.text,
                # extensions=resp.extensions,
                # default_encoding=resp.default_encoding
            )
            return api_response
        except Exception as e:
            logger.error(str(e))
            return e

    async def run_tool(self, action_config: APIRequest) -> APIResponse | Exception:
        try:
            # config_type = ActionText2textAPI.get_config_type()
            config = await ActionText2textAPI.create_config(action_config)
            config_dict = config.model_dump(exclude_none=True)
            auth_header = await self.get_auth_header(config)
            config_dict["headers"] |= auth_header
            if config.body:
                config_dict.pop("body")
                config_dict["content"] = json.dumps(config.body)
                config_dict["headers"]["Content-type"] = "application/json"

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
            return api_response
        except Exception as e:
            logger.error(str(e))
            return e

    async def get_auth_header(self, config: APIRequest) -> typing.Dict[str, str]:
        ctx = Context()
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
