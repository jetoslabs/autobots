from functools import lru_cache

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from autobots.core.settings import get_settings


@lru_cache
def get_mongo_client() -> MongoClient:
    # moved ?retryWrites=true&w=majority out of secrets as github unable to handle it
    # TODO: move it back to secrets
    client = MongoClient(f"{get_settings().MONGO_CONN}?retryWrites=true&w=majority")
    return client


def close_mongo_client():
    get_mongo_client().close()


def get_mongo_db() -> [Database, None, None]:
    db = get_mongo_client()[get_settings().MONGO_DATABASE]
    yield db


def get_mongo_db_collection(db: Database, collection_name: str) -> Collection:
    return db[collection_name]
