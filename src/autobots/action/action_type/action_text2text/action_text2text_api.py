import typing
from typing import Type

import httpx
from httpx._types import RequestData, PrimitiveData
from pydantic import BaseModel, ConfigDict

from src.autobots.action.action_type.abc.IAction import IAction, ActionInputType, ActionOutputType, ActionConfigType, \
    ActionConfigUpdateType, ActionConfigCreateType


class APIRequest(BaseModel):
    method: str
    url: str
    content: typing.Optional[str] = None
    data: typing.Optional[typing.Mapping[str, typing.Any]] = None
    files: typing.Optional[typing.Mapping[str, typing.IO[bytes]]] = None
    json: typing.Optional[typing.Any] = None
    params: typing.Optional[typing.Mapping[str, typing.Union[PrimitiveData]]] = None
    headers: typing.Optional[typing.Mapping[str, str]] = None
    cookies: typing.Optional[typing.Dict[str, str]] = None
    auth: typing.Union[typing.Tuple[typing.Union[str, bytes], typing.Union[str, bytes]]] = None
    follow_redirects: typing.Union[bool] = False
    timeout: typing.Optional[float] = None
    extensions: typing.Optional[typing.MutableMapping[str, typing.Any]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)



class APIRequestData(BaseModel):
    data: typing.Optional[RequestData] = None


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
    IAction[APIRequest, APIRequest, APIRequest, APIRequestData, APIResponse]
):

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return APIRequest

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return APIRequest

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return APIRequest

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return APIRequestData

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return APIResponse

    def __init__(self, action_config: APIRequest):
        super().__init__(action_config)

    async def run_action(self, action_input: APIRequestData) -> APIResponse:
        if action_input.data:
            self.action_config.data = action_input.data
        client = httpx.AsyncClient()
        resp = await client.request(**self.action_config.model_dump(exclude_none=True))
        api_response = APIResponse(
            status_code=resp.status_code,
            headers=resp.headers,
            content=resp.content,
            text=resp.text,
            extensions=resp.extensions,
            default_encoding=resp.default_encoding
        )
        return api_response
