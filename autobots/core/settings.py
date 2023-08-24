from functools import lru_cache

from jose.constants import ALGORITHMS
from pydantic_settings import BaseSettings

from autobots.core.log import log


class Settings(BaseSettings):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_RELOAD: bool = True
    APP_LOG_LEVEL: str = "debug"
    APP_WORKERS: int = 1

    SQLALCHEMY_DATABASE_URL: str = None
    SQLALCHEMY_DATABASE_SCHEMA: str = "backend"

    SUPABASE_URL: str = None
    SUPABASE_ANON_KEY: str = None

    JWT_SECRET_KEY: str = None
    JWT_ALGORITHM: str = ALGORITHMS.HS256

    MONGO_CONN: str = None
    MONGO_DATABASE: str = "backend"

    OPENAI_ORG_ID: str = None
    OPENAI_API_KEY: str = None
    OPENAI_ENGINE: str = "gpt-4"

    STABILITY_HOST: str = None
    STABILITY_KEY: str = None

    UNSPLASH_ACCESS_KEY: str = None
    # UNSPLASH_SECRET_KEY: str = None

    AWS_ACCESS_KEY_ID: str = None
    AWS_SECRET_ACCESS_KEY: str = None
    AWS_S3_BUCKET_NAME: str = None
    AWS_S3_BUCKET_REGION: str = None

    PINECONE_ENVIRONMENT: str = None
    PINECONE_API_KEY: str = None

    DATASTORE_IDENTIFIER: str = "datastore"

    API_v1: str = "/v1"
    API_Hello: str = "/hello"
    API_AUTH: str = "/auth"
    API_AUTH_TOKEN: str = "/token"
    API_ACTIONS: str = "/actions"
    API_PROMPTS: str = "/prompts"
    API_GRAPHS: str = "/graphs"

    class ConfigDict:
        # env_file = f"../.env.local"
        env_file_encoding = 'utf-8'


@lru_cache
def get_settings(_env_file: str = '../.env.local') -> Settings:
    settings = Settings(_env_file=_env_file)
    check_for_none(settings)
    return settings


def check_for_none(settings: Settings):
    for field in settings.__dict__.keys():
        if settings.__dict__[field] is None:
            log.warning(f"Field: {field} is not set")

