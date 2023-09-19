from enum import Enum
from functools import lru_cache

from pydantic import BaseModel


class AppEnv(str, Enum):
    dev = "dev"
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
    gpt_4 = "gpt-4"


class Config(BaseModel):
    APP_ENV: AppEnv = AppEnv
    LOG_LEVEL: LogLevel = LogLevel
    OPENAI_ENGINE: OpenaiEngine = OpenaiEngine


@lru_cache
def get_config():
    return Config()
