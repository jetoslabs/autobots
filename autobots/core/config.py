from enum import Enum
from functools import lru_cache

from pydantic import BaseModel


class OpenaiEngine(str, Enum):
    gpt_3_5 = "gpt-3.5-turbo-16k-0613"
    gpt_4 = "gpt-4"


class Config(BaseModel):
    OPENAI_ENGINE: OpenaiEngine = OpenaiEngine


@lru_cache
def get_config():
    return Config()


