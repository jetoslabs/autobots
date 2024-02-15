import pytest

from src.autobots.conn.openai.openai_client import get_openai
from src.autobots.conn.openai.openai_embeddings.embedding_model import (
    EmbeddingReq,
    EmbeddingRes,
)


@pytest.mark.asyncio
async def test_embedding_happy_path(set_test_settings):
    texts = ["Hello", "World"]
    embedding_req = EmbeddingReq(input=texts)

    resp: EmbeddingRes = await get_openai().openai_embeddings.embeddings(
        embedding_req=embedding_req
    )

    assert len(resp.data) == 2
    assert len(resp.data[0].embedding) == 1536
    assert len(resp.data[1].embedding) == 1536
