from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_RELOAD: bool = True
    APP_LOG_LEVEL: str = "debug"
    APP_WORKERS: int = 1

    OPENAI_ORG_ID: str
    OPENAI_API_KEY: str

    STABILITY_HOST: str
    STABILITY_KEY: str

    UNSPLASH_ACCESS_KEY: str
    # UNSPLASH_SECRET_KEY: str

    API_v1: str = "/v1"
    API_Hello: str = "/hello"

    class Config:
        # env_file = f"../.env.local"
        env_file_encoding = 'utf-8'


@lru_cache
def get_settings(_env_file: str = '../.env.local') -> Settings:
    return Settings(_env_file=_env_file)
