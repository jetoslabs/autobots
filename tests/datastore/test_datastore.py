from typing import List

import pytest
import pytest_asyncio

from autobots.core.settings import get_settings
from autobots.datastore.datastore import Datastore


@pytest_asyncio.fixture
async def set_openai():
    settings = get_settings(_env_file='../.env.local')


@pytest.mark.asyncio
async def test_datastore_happy_path(set_openai):
    str1 = "Delhi,officially the National Capital Territory (NCT) of Delhi, is a city and a union territory of India containing New Delhi, the capital of India. Straddling the Yamuna river, primarily its western or right bank, Delhi shares borders with the state of Uttar Pradesh in the east and with the state of Haryana in the remaining directions. The NCT covers an area of 1,484 square kilometres (573 sq mi). According to the 2011 census, Delhi's city proper population was over 11 million, while the NCT's population was about 16.8 million. Delhi's urban agglomeration, which includes the satellite cities Ghaziabad, Faridabad, Gurgaon and Noida in an area known as the National Capital Region (NCR), has an estimated population of over 28 million, making it the largest metropolitan area in India and the second-largest in the world"
    str2 = "San Francisco, officially the City and County of San Francisco, is a commercial, financial, and cultural center of Northern California. The city proper is the fourth most populous in California, with 808,437 residents as of 2022, and covers a land area of 46.9 square miles (121 square kilometers), at the end of the San Francisco Peninsula, making it the second most densely populated large U.S. city after New York City and the fifth-most densely populated U.S. county, behind only four of the five New York City boroughs. Among the 91 U.S. cities proper with over 250,000 residents, San Francisco was ranked first by per capita income and sixth by aggregate income as of 2021. Colloquial nicknames for San Francisco include Frisco, San Fran, The City, and SF."
    query = "Indian cities"

    datastore = Datastore().init(name="teststore")
    # connect between data in s3 and embedding in pinecone depends on this!
    assert datastore._get_s3_basepath() == datastore._get_pinecone_namespace()

    try:
        await datastore.put(str1)
        await datastore.put(str2)

        result: List[str] = await datastore.search(query=query)

        assert len(result) > 0

        assert result[0] == str1
        assert result[1] == str2

        # testing hydrated datastore
        hydrated_datastore = Datastore().hydrate(datastore_id=datastore.id)
        assert hydrated_datastore.id == datastore.id
        assert hydrated_datastore.trace == datastore.trace
        assert hydrated_datastore.name == datastore.name

        result_from_hydrated: List[str] = await hydrated_datastore.search(query=query)

        assert len(result_from_hydrated) > 0

        assert result_from_hydrated[0] == str1
        assert result_from_hydrated[1] == str2

    finally:
        # cleanup datastore
        deleted = await datastore.empty_and_close()
