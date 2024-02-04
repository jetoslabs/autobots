from loguru import logger
from openai import AsyncOpenAI
from openai.types import CreateEmbeddingResponse
from retry import retry

from src.autobots.conn.openai.openai_embeddings.embedding_model import EmbeddingReq, EmbeddingRes


class OpenaiEmbeddings():

    def __init__(self, client: AsyncOpenAI):
        self.client = client

    @retry(exceptions=Exception, tries=15, delay=40)
    async def embeddings(self, embedding_req: EmbeddingReq) -> EmbeddingRes | None:
        try:
            logger.trace("Starting OpenAI Embedding")
            res: CreateEmbeddingResponse = await self.client.embeddings.create(**embedding_req.model_dump())
            logger.trace("Completed OpenAI Embedding")
            resp: EmbeddingRes = EmbeddingRes(**res.model_dump())
            return resp
        except Exception as e:
            logger.error(str(e))
            raise
