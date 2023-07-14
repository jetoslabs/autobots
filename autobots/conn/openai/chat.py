from enum import Enum
from typing import List

from pydantic import BaseModel


class Role(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class Message(BaseModel):
    role: str | Role
    content: str


class ChatReq(BaseModel):
    model: str = "gpt-4"
    messages: List[Message]
    temperature: int = 0.8
    top_p: int = 1
    n: int = 1
    stream: bool = False
    stop: str | List[str] | None = None
    max_tokens: int = 2000
    presence_penalty: int = 0
    frequency_penalty: int = 0
    # logit_bias: str | None = None
    user: str = ""


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
