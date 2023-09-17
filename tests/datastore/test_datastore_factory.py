import pytest
import pytest_asyncio

from autobots.core.settings import get_settings
from autobots.datastore.datastore_factory import DatastoreFactory, get_datastore_factory


@pytest_asyncio.fixture
async def set_openai():
    settings = get_settings(_env_file='../.env.local')


@pytest.mark.asyncio
async def test_datastore_happy_path(set_openai):
    str1 = "The truth is one, the wise call it by many names. ― Rig Veda"
    str2 = "One who talks sweet, spend all their days in happiness. – Rig Veda"
    str3 = "One has to be humble if he desires to acquire knowledge. – Rig Veda"

    datastore = await get_datastore_factory().create_datastore("test_datastore_happy_path")
    try:

        await datastore.put_data(str1)
        await datastore.put_data(str2)
        await datastore.put_data(str3)

        search_res = await datastore.search("How to be happy?", top_k=1)

        assert len(search_res) == 1
        assert search_res[0] == str2

    finally:
        await datastore.empty_and_close()
