from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_RELOAD: bool = True
    APP_LOG_LEVEL: str = "debug"
    APP_WORKERS: int = 1


settings = Settings()
