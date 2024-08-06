from abc import abstractmethod
from typing import TypeVar, Type

from pydantic import BaseModel

from src.autobots.secret.app_types import AppTypes

CredsModelType = TypeVar("CredsModelType", bound=BaseModel)


class AppCredsTypeABC:

    @staticmethod
    @abstractmethod
    def get_app() -> AppTypes: ...

    @staticmethod
    @abstractmethod
    def get_cred_model_type() -> Type[CredsModelType]: ...
