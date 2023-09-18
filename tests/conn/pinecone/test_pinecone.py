import pytest as pytest
import pytest_asyncio

from autobots.conn.pinecone.pinecone import get_pinecone
from autobots.core.settings import get_settings
from autobots.core.utils import gen_hash


@pytest_asyncio.fixture
async def set_openai():
    settings = get_settings(_env_file='.env.local')


@pytest.mark.asyncio
async def test_pinecone_happy_path(set_openai):
    str1 = "Delhi,officially the National Capital Territory (NCT) of Delhi, is a city and a union territory of India containing New Delhi, the capital of India. Straddling the Yamuna river, primarily its western or right bank, Delhi shares borders with the state of Uttar Pradesh in the east and with the state of Haryana in the remaining directions. The NCT covers an area of 1,484 square kilometres (573 sq mi). According to the 2011 census, Delhi's city proper population was over 11 million, while the NCT's population was about 16.8 million. Delhi's urban agglomeration, which includes the satellite cities Ghaziabad, Faridabad, Gurgaon and Noida in an area known as the National Capital Region (NCR), has an estimated population of over 28 million, making it the largest metropolitan area in India and the second-largest in the world"
    str2 = "San Francisco, officially the City and County of San Francisco, is a commercial, financial, and cultural center of Northern California. The city proper is the fourth most populous in California, with 808,437 residents as of 2022, and covers a land area of 46.9 square miles (121 square kilometers), at the end of the San Francisco Peninsula, making it the second most densely populated large U.S. city after New York City and the fifth-most densely populated U.S. county, behind only four of the five New York City boroughs. Among the 91 U.S. cities proper with over 250,000 residents, San Francisco was ranked first by per capita income and sixth by aggregate income as of 2021. Colloquial nicknames for San Francisco include Frisco, San Fran, The City, and SF."
    query = "Indian cities"

    str1_id = gen_hash(str1)
    str2_id = gen_hash(str2)

    namespace = "default"

    try:

        await get_pinecone().upsert_data(str1_id, str1, metadata={"type": "places"}, namespace=namespace)
        await get_pinecone().upsert_data(str2_id, str2, metadata={"type": "places"}, namespace=namespace)

        query_res = await get_pinecone().query(data=query, top_k=2, namespace=namespace)
        assert len(query_res) == 2

        vec_id = query_res[0].id
        assert str1_id == vec_id

    finally:

        await get_pinecone().delete_all(namespace=namespace)
