from enum import Enum
from typing import List

from pydantic import BaseModel

from autobots.core.config import OpenaiEngine, get_config


class Role(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class Message(BaseModel):
    role: Role
    content: str


class ChatReq(BaseModel):
    # model: str = get_settings().OPENAI_ENGINE  # "gpt-4"
    model: OpenaiEngine = get_config().OPENAI_ENGINE.gpt_3_5
    messages: List[Message]
    temperature: float = 0.8
    top_p: int = 1
    n: int = 1
    stream: bool = False
    stop: str | List[str] | None = "stop"
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
