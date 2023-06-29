
import pytest
import pytest_asyncio

from autobots.conn.conn import get_conn
from autobots.conn.openai.embedding import EmbeddingRes, EmbeddingReq
from autobots.core.settings import get_settings


# Run command `pytest -vv -n 5` from `autobots/tests` folder
@pytest_asyncio.fixture
async def set_openai():
    settings = get_settings(_env_file='../.env.local')


@pytest.mark.asyncio
async def test_embedding_happy_path(set_openai):
    texts = ["Hello", "World"]
    embedding_req = EmbeddingReq(input=texts)

    resp: EmbeddingRes = await get_conn().open_ai.embedding(embedding_req=embedding_req)

    assert len(resp.data) == 2
    assert len(resp.data[0].embedding) == 1536
    assert len(resp.data[1].embedding) == 1536
