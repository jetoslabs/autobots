from typing import Any, List

from src.autobots.crud.crud_protocol import CRUDProtocol, DataType, LiteDataType, DataCreateType, DataFindType, \
    DataUpdateType, FindManyData, FindPageData, FindOneData, ReadByIdData, CreateData


class CRUDS3(CRUDProtocol[DataType, LiteDataType, DataCreateType, DataFindType, DataUpdateType]):
    @staticmethod
    async def create(create_data: List[CreateData]) -> List[DataType | Exception]:
        raise NotImplementedError

    @staticmethod
    async def _read_by_id(read_data: ReadByIdData) -> DataType | Exception:
        raise NotImplementedError

    @staticmethod
    async def find_one(find_data: FindOneData) -> DataType | Exception:
        raise NotImplementedError

    @staticmethod
    async def find_many(find_data: FindManyData) -> List[LiteDataType] | Exception:
        raise NotImplementedError

    @staticmethod
    async def find_paginated(find_paginated_data: FindManyData) -> FindPageData | Exception:
        raise NotImplementedError

    @staticmethod
    async def update(update_data: List[DataUpdateType]) -> List[DataType | Exception]:
        raise NotImplementedError

    @staticmethod
    async def delete_many(find_data: FindManyData) -> Any | Exception:
        raise NotImplementedError

    @staticmethod
    async def count(find_data: FindManyData) -> int | Exception:
        raise NotImplementedError
