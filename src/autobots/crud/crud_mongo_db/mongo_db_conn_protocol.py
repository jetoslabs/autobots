from typing import Protocol

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

from src.autobots.data_model.context import Context
from src.autobots.core.settings import Settings


class MongoDBConnProtocol(Protocol):

    @staticmethod
    async def client() -> AsyncIOMotorClient: ...

    @staticmethod
    async def _client(ctx: Context, settings: Settings) -> AsyncIOMotorClient: ...

    @staticmethod
    async def close_client(ctx: Context, client: AsyncIOMotorClient) -> None: ...

    @staticmethod
    async def database(ctx: Context, settings: Settings, client: AsyncIOMotorClient) -> AsyncIOMotorDatabase: ...

    @staticmethod
    async def collection(ctx: Context, settings: Settings, AsyncIOMotorDatabase, collection_name: str) -> AsyncIOMotorCollection: ...
