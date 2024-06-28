from typing import Any

from src.autobots.crud.crud_protocol import CRUDProtocol, DataType, LiteDataType, DataCreateType, DataFindType, \
    DataUpdateType


class VectorSearchProtocol(
    CRUDProtocol[DataType, LiteDataType, DataCreateType, DataFindType, DataUpdateType],
):
    @staticmethod
    async def vector_search(**kwargs) -> Any: ...
