from functools import lru_cache

from openai import AsyncOpenAI
from openai.types import CreateEmbeddingResponse, ImagesResponse

from autobots.conn.openai.embedding import EmbeddingReq, EmbeddingRes
from autobots.conn.openai.image_model import ImageReq
from autobots.conn.openai.openai_audio.openai_audio import OpenaiAudio
from autobots.conn.openai.openai_chat.openai_chat import OpenaiChat
from autobots.core.log import log
from autobots.core.settings import Settings, SettingsProvider


class OpenAI:

    def __init__(self, org_id: str, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key,organization=org_id,timeout=180)
        self.openai_audio = OpenaiAudio(self.client)
        self.openai_chat = OpenaiChat(self.client)

    async def embedding(self, embedding_req: EmbeddingReq) -> EmbeddingRes | None:
        try:
            log.trace("Starting OpenAI Embedding")
            res: CreateEmbeddingResponse = await self.client.embeddings.create(**embedding_req.model_dump())
            log.trace("Completed OpenAI Embedding")
            resp: EmbeddingRes = EmbeddingRes(**res.model_dump())
            return resp
        except Exception as e:
            log.exception(e)

    async def create_image(self, image_req: ImageReq) -> ImagesResponse | None:
        try:
            log.trace("Starting OpenAI create image")
            res: ImagesResponse = await self.client.images.generate(**image_req.model_dump())
            log.trace("Completed OpenAI create image")
            return res
        except Exception as e:
            log.exception(e)


@lru_cache
def get_openai(settings: Settings = SettingsProvider.sget()) -> OpenAI:
    return OpenAI(settings.OPENAI_ORG_ID, settings.OPENAI_API_KEY)
