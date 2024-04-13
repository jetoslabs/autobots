from functools import lru_cache

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import MongoClient

from src.autobots.core.settings import SettingsProvider


@lru_cache
def get_mongo_client() -> AsyncIOMotorClient:
    mongo_conn = SettingsProvider.sget().MONGO_CONN
    # moved ?retryWrites=true&w=majority out of secrets as github unable to handle it
    # TODO: move it back to secrets
    client = AsyncIOMotorClient(f"{mongo_conn}?retryWrites=true&w=majority")
    return client


def close_mongo_client():
    get_mongo_client().close()


def get_mongo_db() -> [AsyncIOMotorDatabase, None, None]:
    db = get_mongo_client()[SettingsProvider.sget().MONGO_DATABASE]
    yield db


def get_mongo_db_collection(db: AsyncIOMotorDatabase, collection_name: str) -> AsyncIOMotorCollection:
    return db[collection_name]


# PYMONGO client is only used in APScheduler

@lru_cache
def get_pymongo_client() -> MongoClient:
    mongo_conn = SettingsProvider.sget().MONGO_CONN
    client = MongoClient(f"{mongo_conn}?retryWrites=true&w=majority")
    return client


def close_pymongo_client():
    get_pymongo_client().close()
