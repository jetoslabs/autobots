import time
from functools import lru_cache

import openai
from openai.openai_object import OpenAIObject

from autobots.conn.openai.chat import ChatReq, ChatRes
from autobots.conn.openai.embedding import EmbeddingReq, EmbeddingRes
from autobots.core.log import log
from autobots.core.settings import get_settings, Settings


class OpenAI:

    def __init__(self, org_id: str = get_settings().OPENAI_ORG_ID, api_key: str = get_settings().OPENAI_API_KEY):
        # once set, any invocation of openai has state
        # openai here is global
        openai.organization = org_id
        openai.api_key = api_key

    async def chat(self, chat_req: ChatReq) -> ChatRes:
        max_retry = 3
        for i in range(max_retry):
            try:
                log.trace("Starting OpenAI Chat, try: 1")
                res: OpenAIObject = await openai.ChatCompletion.acreate(**chat_req.dict(), timeout=30)
                log.trace("Completed OpenAI Chat")
                resp: ChatRes = ChatRes(**res.to_dict())
                return resp
            except Exception as e:
                log.error(e)
                time.sleep(60)

    async def embedding(self, embedding_req: EmbeddingReq) -> EmbeddingRes:
        try:
            log.trace("Starting OpenAI Embedding")
            res: OpenAIObject = await openai.Embedding.acreate(**embedding_req.dict())
            log.trace("Completed OpenAI Embedding")
            resp: EmbeddingRes = EmbeddingRes(**res.to_dict())
            return resp
        except Exception as e:
            log.error(e)


@lru_cache
def get_openai(settings: Settings = get_settings()) -> OpenAI:
    return OpenAI()
