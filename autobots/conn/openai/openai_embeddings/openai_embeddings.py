from openai import AsyncOpenAI
from openai.types import CreateEmbeddingResponse

from autobots.conn.openai.openai_embeddings.embedding_model import EmbeddingReq, EmbeddingRes
from autobots.core.log import log


class OpenaiEmbeddings():

    def __init__(self, client: AsyncOpenAI):
        self.client = client

    async def embeddings(self, embedding_req: EmbeddingReq) -> EmbeddingRes | None:
        try:
            log.trace("Starting OpenAI Embedding")
            res: CreateEmbeddingResponse = await self.client.embeddings.create(**embedding_req.model_dump())
            log.trace("Completed OpenAI Embedding")
            resp: EmbeddingRes = EmbeddingRes(**res.model_dump())
            return resp
        except Exception as e:
            log.exception(str(e))
