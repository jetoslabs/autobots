import typing
from typing import Type

import httpx
from httpx._types import PrimitiveData
from loguru import logger
from pydantic import BaseModel, ConfigDict

from src.autobots.action.action_type.abc.ActionABC import ActionABC


class APIRequest(BaseModel):
    method: str
    url: str
    content: typing.Optional[str] = None
    data: typing.Optional[typing.Mapping[str, typing.Any]] = None
    files: typing.Optional[typing.Mapping[str, typing.IO[bytes]]] = None
    req_json: typing.Optional[typing.Any] = None
    params: typing.Optional[typing.Mapping[str, typing.Union[PrimitiveData]]] = None
    headers: typing.Optional[typing.Mapping[str, str]] = None
    cookies: typing.Optional[typing.Dict[str, str]] = None
    auth: typing.Union[typing.Tuple[typing.Union[str, bytes], typing.Union[str, bytes]]] = None
    follow_redirects: typing.Union[bool] = False
    timeout: typing.Optional[float] = None
    extensions: typing.Optional[typing.MutableMapping[str, typing.Any]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class APIInput(APIRequest):
    method: typing.Optional[str] = None
    url: typing.Optional[str] = None


class APIResponse(BaseModel):
    status_code: int
    headers: typing.Optional[typing.Mapping[str, str]] = None
    content: typing.Optional[str] = None
    text: typing.Optional[str] = None
    # stream: typing.Union[SyncByteStream, AsyncByteStream, None] = None
    # request: typing.Optional[Request] = None
    extensions: typing.Optional[typing.MutableMapping[str, typing.Any]] = None
    # history: typing.Optional[typing.List["Response"]] = None
    default_encoding: str = "utf-8"

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ActionText2textAPI(
    ActionABC[APIRequest, APIRequest, APIRequest, APIInput, APIResponse]
):
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
    def update_config(config: APIRequest, config_update: APIInput) -> APIRequest:
        if config_update.data:
            config.data = config_update.data
        # TODO: update config for all APIInput fields
        return config

    def __init__(self, action_config: APIRequest):
        super().__init__(action_config)

    async def run_action(self, action_input: APIInput) -> APIResponse | Exception:
        try:
            config = ActionText2textAPI.update_config(self.action_config, action_input)
            client = httpx.AsyncClient()
            resp = await client.request(**config.model_dump(exclude_none=True))
            api_response = APIResponse(
                status_code=resp.status_code,
                headers=resp.headers,
                content=resp.content,
                text=resp.text,
                extensions=resp.extensions,
                default_encoding=resp.default_encoding
            )
            return api_response
        except Exception as e:
            logger.error(str(e))
            return e

    @staticmethod
    async def create_and_run_action(action_config: APIRequest) -> APIResponse | Exception:
        try:
            config_type = ActionText2textAPI.get_config_type()
            config_dict = ActionText2textAPI.create_config(action_config)
            config = config_type.model_validate(config_dict)

            action = ActionText2textAPI(config)
            action_input = APIInput()
            output = await action.run_action(action_input)
            return output
        except Exception as e:
            logger.error(str(e))
            return e

