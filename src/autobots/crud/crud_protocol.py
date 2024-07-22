from typing import Protocol, TypeVar, List, Any, Type

from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel, ConfigDict

from src.autobots.data_model.context import ContextData

DataType = TypeVar("DataType", bound=BaseModel)
# LiteDataType is minimal version of DocType, used in listing. Takes less memory.
LiteDataType = TypeVar("LiteDataType", bound=BaseModel)
DataCreateType = TypeVar("DataCreateType", bound=BaseModel)
DataFindType = TypeVar("DataFindType", bound=BaseModel)
DataUpdateType = TypeVar("DataUpdateType", bound=BaseModel)


class FindPageData(BaseModel):
    docs: List[LiteDataType]
    total_count: int
    limit: int
    offset: int


class CrudBaseData(ContextData):
    data_source: AsyncIOMotorCollection #TODO add more sources like sql, s3, https
    data_type: Type[DataType]
    lite_data_type: Type[LiteDataType]

    model_config = ConfigDict(arbitrary_types_allowed=True)


class CreateData(CrudBaseData):
    create_params: DataCreateType


class ReadByIdData(CrudBaseData):
    read_id: str


class ReadData(CrudBaseData):
    read_params: DataCreateType


class FindOneData(CrudBaseData):
    find_params: DataFindType
    or_find_queries: List[DataFindType] | None = None


class FindManyData(FindOneData):
    limit: int = 100,
    offset: int = 0


class UpdateData(CrudBaseData):
    update_params: DataUpdateType


class CRUDProtocol(Protocol[DataType, LiteDataType, DataCreateType, DataFindType, DataUpdateType]):
    """Protocol for CRUD."""

    @staticmethod
    async def create(create_data: List[CreateData]) -> List[DataType | Exception]: ...

    @staticmethod
    async def _read_by_id(read_data: ReadByIdData) -> DataType | Exception: ...

    @staticmethod
    async def find_one(find_data: FindOneData) -> DataType | Exception: ...

    @staticmethod
    async def find_many(find_data: FindManyData) -> List[LiteDataType] | Exception: ...

    @staticmethod
    async def find_paginated(find_paginated_data: FindManyData) -> FindPageData | Exception: ...

    @staticmethod
    async def update(update_data: List[DataUpdateType]) -> List[DataType | Exception]: ...

    @staticmethod
    async def delete_many(find_data: FindManyData) -> Any | Exception: ...

    @staticmethod
    async def count(find_data: FindManyData) -> int | Exception: ...
