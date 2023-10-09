from functools import lru_cache
from typing import List

from jose.constants import ALGORITHMS
from loguru import logger
from pydantic_settings import BaseSettings

from autobots.core.config import get_config


class Settings(BaseSettings):
    ENV: str = get_config().APP_ENV.prod
    # value from github deployment action (CICD)
    VERSION: str = "local"

    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_RELOAD: bool = True
    APP_LOG_LEVEL: str = "debug"
    APP_WORKERS: int = 1

    COOKIE_DOMAIN: str = "127.0.0.1"
    ALLOW_ORIGINS: str = "http://localhost:3000"
    ALLOWED_ORIGINS: List[str] = ALLOW_ORIGINS.split(",")

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
    # OPENAI_ENGINE: str = "gpt-3.5-turbo-16k-0613"  # "gpt-4"

    STABILITY_HOST: str = None
    STABILITY_KEY: str = None

    UNSPLASH_ACCESS_KEY: str = None
    # UNSPLASH_SECRET_KEY: str = None

    AWS_ACCESS_KEY_ID: str = None
    AWS_SECRET_ACCESS_KEY: str = None
    AWS_S3_BUCKET_NAME: str = None
    AWS_S3_BUCKET_REGION: str = None

    AWS_S3_PUBLIC_BUCKET_NAME: str = None
    AWS_S3_PUBLIC_BUCKET_IMAGE_FOLDER: str = None

    PINECONE_ENVIRONMENT: str = None
    PINECONE_API_KEY: str = None

    UNSTRUCTURED_API_KEY: str = None

    DATASTORE_IDENTIFIER: str = "datastore"

    API_v1: str = "/v1"
    API_Hello: str = "/hello"
    API_AUTH: str = "/auth"
    API_AUTH_TOKEN: str = "/token"
    API_ACTIONS: str = "/actions"
    API_ACTION_GRAPHS: str = "/action_graphs"
    API_PROMPTS: str = "/prompts"
    API_DATASTORE: str = "/datastore"
    API_CHAT: str = "/chat"
    API_AGENTS: str = "/agents"
    API_GRAPHS: str = "/graphs"

    class ConfigDict:
        # env_file = f".env.local"
        env_file_encoding = 'utf-8'


@lru_cache
def get_settings(_env_file: str = '.env.local') -> Settings:
    settings = Settings(_env_file=_env_file)
    check_for_none(settings)
    logger.bind(app="autobots", ALLOWED_ORIGINS=settings.ALLOWED_ORIGINS)
    return settings


def check_for_none(settings: Settings):
    for field in settings.__dict__.keys():
        if settings.__dict__[field] is None:
            logger.warning(f"Field: {field} is not set")

