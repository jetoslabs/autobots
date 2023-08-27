from functools import lru_cache

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from autobots.core.settings import get_settings


@lru_cache
def get_mongo_client() -> MongoClient:
    client = MongoClient(get_settings().MONGO_CONN)
    return client


def close_mongo_client():
    get_mongo_client().close()


def get_mongo_db() -> [Database, None, None]:
    db = get_mongo_client()[get_settings().MONGO_DATABASE]
    yield db


def get_mongo_db_collection(db: Database, collection_name: str) -> Collection:
    return db[collection_name]
