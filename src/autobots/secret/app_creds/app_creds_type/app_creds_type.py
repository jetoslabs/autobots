from abc import abstractmethod
from typing import TypeVar, Type

from pydantic import BaseModel

from src.autobots.secret.app_creds.apps_enum import APPS_ENUM

CredsModelType = TypeVar("CredsModelType", bound=BaseModel)


class AppCredsType:

    @staticmethod
    @abstractmethod
    def get_app() -> APPS_ENUM: ...

    @staticmethod
    @abstractmethod
    def get_cred_model_type() -> Type[CredsModelType]: ...
