from enum import Enum
from typing import List, Union, Literal, Optional, Dict

import httpx
from pydantic import BaseModel, ConfigDict

class ToolParam(BaseModel):
    name: str
    description: Optional[str] = None
class Role(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class Message(BaseModel):
    role: Role
    content: str


class ChatReq(BaseModel):
    messages: List[Message]
    model: Literal[
        "claude-2",
        "claude-instant",
        "claude-1",
        "claude-1.2",
        "claude-1.3",
        "claude-1.3-100k",
        "claude-3-5-sonnet-20240620"
    ] = "claude-2"
    temperature: Optional[float] = 0.8
    max_tokens: Optional[int] = 2000
    top_p: Optional[float] = None
    tools: List[str] | List[str] | None = None
    top_k: Optional[int] = None
    stream: Optional[Literal[False]] | Literal[True] = False
    stop: Union[Optional[str], List[str]] = None
    user: str | None = None
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
