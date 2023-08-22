from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from autobots.core.settings import get_settings


def get_mongo_db() -> [Database, None, None]:
    client = MongoClient(get_settings().MONGO_CONN)
    db = client[get_settings().MONGO_DATABASE]
    try:
        yield db
    finally:
        db.close()


def get_mongo_db_collection(db: Database, collection_name: str) -> Collection:
    return db[collection_name]
