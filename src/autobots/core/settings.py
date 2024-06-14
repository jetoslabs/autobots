from functools import lru_cache
from typing import List, Literal

from jose.constants import ALGORITHMS
from loguru import logger
from pydantic_settings import BaseSettings

# from autobots.core.config import get_config


# def get_env_suffix(ENV):
#     return f"_{ENV}" if ENV != "prod" else ""


class Settings(BaseSettings):
    ENV: Literal["local", "test", "dev", "qa", "stage", "prod"] | str = "local"

    # value from github deployment action (CICD)
    VERSION: str = "local"

    # APP_HOST: str = "0.0.0.0"
    # APP_PORT: int = 8000
    # APP_RELOAD: bool = True
    # APP_LOG_LEVEL: str = "debug"
    # APP_WORKERS: int = 1

    COOKIE_DOMAIN: str = "localhost"
    ALLOW_ORIGINS: str = "http://localhost:3000"
    ALLOWED_ORIGINS: List[str] = ALLOW_ORIGINS.split(",")

    SQLALCHEMY_DATABASE_URL: str
    SQLALCHEMY_DATABASE_SCHEMA: str

    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = ALGORITHMS.HS256

    MONGO_CONN: str
    MONGO_DATABASE: str

    OPENAI_ORG_ID: str = None
    OPENAI_API_KEY: str = None

    STABILITY_HOST: str = None
    STABILITY_KEY: str = None
    STABLE_DIFFUSION_API_KEY: str = None

    UNSPLASH_ACCESS_KEY: str = None

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_S3_BUCKET_NAME: str
    AWS_S3_BUCKET_REGION: str

    AWS_S3_PUBLIC_BUCKET_NAME: str
    AWS_S3_PUBLIC_BUCKET_IMAGE_FOLDER: str
    AWS_S3_FILES_FOLDER: str = "files"

    TEMPORARY_DIR: str = "to_del"

    PINECONE_ENVIRONMENT: str = None
    PINECONE_API_KEY: str = None

    UNSTRUCTURED_API_KEY: str = None

    REPLICATE_API_KEY: str = None

    DATASTORE_IDENTIFIER: str = "datastore"

    SCHEDULE_JOBSTORE_MONGO_DB_COLLECTION_NAME: str = "_APSCHEDULER_JOBS"

    DISCORD_SERVER_ID: str
    DISCORD_TOKEN: str
    DISCORD_CHANNEL_ID: str
    USEAPI_NET_TOKEN: str
    USEAPI_NET_END_POINT_URL: str
    CLAID_API_KEY: str
    CLAID_SIDE_S3_BUCKET: str
    CLAID_PATH_PREFIX: str

    SERP_API_KEY: str

    API_v1: str = "/v1"
    API_Hello: str = "/hello"
    API_AUTH: str = "/auth"
    API_AUTH_TOKEN: str = "/token"
    API_ACTIONS: str = "/actions"
    API_ACTION_TYPES: str = "/action_types"
    API_ACTIONS_MARKET: str = "/action_market"
    API_ACTION_RESULTS: str = "/action_results"
    API_ACTION_GRAPHS: str = "/action_graphs"
    API_ACTION_GRAPHS_RESULTS: str = "/action_graphs_results"
    API_SCHEDULES: str = "/schedules"
    API_DATASTORE: str = "/datastore"
    API_FILES: str = "/files"
    API_OPENAI_STORAGE: str = "/openai_storage"
    API_ACTION_CHATS: str = "/action_chats"
    API_AGENTS: str = "/agents"
    API_GRAPHS: str = "/graphs"

    class ConfigDict:
        # env_file = f".env.local"
        env_file_encoding = 'utf-8'


class SettingsProvider:
    _env_file: str = None
    _settings: Settings = None

    @staticmethod
    @lru_cache
    def set_env_file(_env_file: str = '.env.local') -> None:
        SettingsProvider._env_file = _env_file

    @staticmethod
    @lru_cache
    def set() -> None:
        SettingsProvider._settings = Settings(_env_file=SettingsProvider._env_file)
        SettingsProvider.check_for_none(SettingsProvider._settings)
        logger.debug(f"Allowed origins: {SettingsProvider._settings.ALLOWED_ORIGINS}")

    @staticmethod
    async def get() -> Settings:
        return SettingsProvider._settings

    @staticmethod
    def sget() -> Settings:
        if not SettingsProvider._settings:
            SettingsProvider.set()
        return SettingsProvider._settings

    @staticmethod
    def check_for_none(settings: Settings):
        for field in settings.__dict__.keys():
            if settings.__dict__[field] is None:
                logger.warning(f"Field: {field} is not set")
