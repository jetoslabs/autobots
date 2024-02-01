from enum import Enum
from functools import lru_cache
from pydantic import BaseModel


class AppEnv(str, Enum):
    local = "local"
    test = "test"
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


class Config(BaseModel):
    APP_ENV: AppEnv = AppEnv.local
    LOG_LEVEL: LogLevel = LogLevel.debug


@lru_cache
def get_config():
    return Config()
