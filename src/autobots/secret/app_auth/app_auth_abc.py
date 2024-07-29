from abc import abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

from src.autobots.data_model.context import Context

AppAuthType = TypeVar("AppAuthType", bound=BaseModel)


class AppAuthABC(Generic[AppAuthType]):

    @staticmethod
    @abstractmethod
    def get_auth_data_type():
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def update_auth_header(ctx: Context, auth: AppAuthType) -> AppAuthType:
        raise NotImplementedError
