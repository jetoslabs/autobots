import pytest
from pymongo.database import Database
from src.autobots.core.utils import gen_random_str
from src.autobots.core.database.mongo_base import get_mongo_db, get_mongo_db_collection


@pytest.mark.asyncio
async def test_mongo_base_happy_path(set_test_settings):
    session: Database = next(get_mongo_db())
    assert session is not None

    collection_name = f"{__name__}_{gen_random_str()}"
    collection = get_mongo_db_collection(session, collection_name)
    try:
        inserted_1 = collection.insert_one({"name": f"{__name__}_1"})
        assert inserted_1 is not None
        inserted_2 = collection.insert_one({"name": f"{__name__}_2"})
        assert inserted_2 is not None

        result = collection.find_one({"name": f"{__name__}_1"})
        assert result.get("name") == f"{__name__}_1"

        results = collection.find({"name": f"{__name__}_1"})
        res = results.next()
        assert res.get("name") == f"{__name__}_1"

    finally:
        session.drop_collection(collection)
