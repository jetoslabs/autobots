from enum import Enum
from typing import List, Union, Literal, Optional, Dict

import httpx
from openai._types import Headers, Query, Body
from openai.types import ChatModel
from openai.types.chat import ChatCompletionMessageParam, completion_create_params, ChatCompletionToolChoiceOptionParam, \
    ChatCompletionToolParam, ChatCompletionMessage
from pydantic import BaseModel, ConfigDict


class Role(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class Message(BaseModel):
    role: Role
    content: Union[str,List[Dict]]


class ChatReq(BaseModel):
    messages: List[Message]
    model: ChatModel = "gpt-4o-mini"
    frequency_penalty: Optional[float] = None
    # function_call: completion_create_params.FunctionCall = None
    # functions: List[completion_create_params.Function] = None
    logit_bias: Optional[Dict[str, int]] = None
    logprobs: Optional[bool] = None
    max_tokens: Optional[int] = 2000
    n: Optional[int] = 1
    presence_penalty: Optional[float] = None
    response_format: Optional[completion_create_params.ResponseFormat] = None
    seed: Optional[int] = None
    stop: Union[Optional[str], List[str]] = "stop"
    stream: Optional[Literal[False]] | Literal[True] = False
    temperature: Optional[float] = 0.8
    tool_choice: ChatCompletionToolChoiceOptionParam | None = None
    tools: List[ChatCompletionToolParam | str] | None = None
    top_logprobs: Optional[int] = None
    top_p: Optional[float] = None
    user: str | None = None
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    extra_headers: Headers | None = None
    extra_query: Query | None = None
    extra_body: Body | None = None
    timeout: float | httpx.Timeout | None = 180

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: str


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatRes(BaseModel):
    id: str
    object: str = None
    created: int
    model: str
    choices: List[Choice]
    usage: Usage
