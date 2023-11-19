from enum import Enum
from functools import lru_cache

from pydantic import BaseModel


class AppEnv(str, Enum):
    dev = "dev"
    qa = "qa"
    stage = "stage"
    prod = "prod"


class LogLevel(str, Enum):
    trace = "TRACE"
    debug = "DEBUG"
    info = "INFO"
    success = "SUCCESS"
    warning = "WARNING"
    error = "ERROR"
    critical = "CRITICAL"


class OpenaiEngine(str, Enum):
    gpt_3_5 = "gpt-3.5-turbo-16k-0613"
    gpt_4_8k = "gpt-4"
    gpt_4_8k_0314 = "gpt-4-0314"
    gpt_4_8k_0613 = "gpt-4-0613"
    gpt_4_32k = "gpt-4-32k"
    gpt_4_32k_0314 = "gpt-4-32k-0314"


class Config(BaseModel):
    APP_ENV: AppEnv = AppEnv
    LOG_LEVEL: LogLevel = LogLevel
    OPENAI_ENGINE: OpenaiEngine = OpenaiEngine


@lru_cache
def get_config():
    return Config()
