import pytest

from src.autobots.datastore.datastore_factory import get_datastore_factory


@pytest.mark.asyncio
async def test_datastore_factory_happy_path(set_test_settings):
    str1 = "The truth is one, the wise call it by many names. ― Rig Veda"
    str2 = "One who talks sweet, spend all their days in happiness. – Rig Veda"
    str3 = "One has to be humble if he desires to acquire knowledge. – Rig Veda"

    datastore = await get_datastore_factory().create_datastore("test_datastore_factory_happy_path")
    try:

        await datastore.put_data(str1)
        await datastore.put_data(str2)
        await datastore.put_data(str3)

        search_res = await datastore.search("How to be happy?", top_k=1)

        assert len(search_res) == 1
        assert search_res[0] == str2

    finally:
        await datastore.empty_and_close()
