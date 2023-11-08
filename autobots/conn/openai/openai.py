import time
from functools import lru_cache
from typing import List

from openai import AsyncOpenAI, AsyncStream
from openai.types import CreateEmbeddingResponse, ImagesResponse
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from autobots.conn.openai.chat import ChatReq
from autobots.conn.openai.embedding import EmbeddingReq, EmbeddingRes
from autobots.conn.openai.image_model import ImageReq, ImageRes
from autobots.core.log import log
from autobots.core.settings import Settings, SettingsProvider


class OpenAI:

    def __init__(self, org_id: str, api_key: str):
        self.client = AsyncOpenAI(
            api_key=api_key,
            organization=org_id,
            timeout=180
        )

    async def chat(self, chat_req: ChatReq) -> ChatCompletion | AsyncStream[ChatCompletionChunk] | None:
        max_retry = 3
        for i in range(max_retry):
            try:
                log.trace("Starting OpenAI Chat, try: 1")
                res: ChatCompletion = await self.client.chat.completions.create(**chat_req.model_dump(), timeout=180)
                log.trace("Completed OpenAI Chat")
                if isinstance(res, AsyncStream):
                    return self.yield_chat_chunks(res)
                else:
                    return res
            except Exception as e:
                log.exception(e)
                time.sleep(5)

    async def yield_chat_chunks(self, chat_res: AsyncStream[ChatCompletionChunk]) -> ChatCompletionChunk | None:
        try:
            async for part in chat_res:
                yield part
        except Exception as e:
            log.exception(e)

    async def embedding(self, embedding_req: EmbeddingReq) -> EmbeddingRes | None:
        try:
            log.trace("Starting OpenAI Embedding")
            res: CreateEmbeddingResponse = await self.client.embeddings.create(**embedding_req.model_dump())
            log.trace("Completed OpenAI Embedding")
            resp: EmbeddingRes = EmbeddingRes(**res.to_dict())
            return resp
        except Exception as e:
            log.exception(e)

    async def create_image(self, image_req: ImageReq) -> List[ImageRes]:
        try:
            log.trace("Starting OpenAI create image")
            res: ImagesResponse = await self.client.images.generate(**image_req.model_dump())
            log.trace("Completed OpenAI create image")
            images = []
            for data in res.data:
                images = images + [ImageRes.model_validate(data)]
            return images
        except Exception as e:
            log.exception(e)


@lru_cache
def get_openai(settings: Settings = SettingsProvider.sget()) -> OpenAI:
    return OpenAI(settings.OPENAI_ORG_ID, settings.OPENAI_API_KEY)
