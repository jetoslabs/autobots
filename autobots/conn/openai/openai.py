import openai
from openai.openai_object import OpenAIObject

from autobots.conn.openai.chat import ChatReq, ChatRes
from autobots.conn.openai.embedding import EmbeddingReq, EmbeddingRes
from autobots.core.log import log
from autobots.core.settings import get_settings


class OpenAI:

    def __init__(self, org_id: str = get_settings().OPENAI_ORG_ID, api_key: str = get_settings().OPENAI_API_KEY):
        # once set, any invocation of openai has state
        # openai here is global
        openai.organization = org_id
        openai.api_key = api_key

    async def chat(self, chat_req: ChatReq) -> ChatRes:
        try:
            log.trace("Starting OpenAI Chat")
            res: OpenAIObject = await openai.ChatCompletion.acreate(**chat_req.dict(), timeout=30)
            log.trace("Completed OpenAI Chat")
            resp: ChatRes = ChatRes(**res.to_dict())
            return resp
        except Exception as e:
            log.error(e)

    async def embedding(self, embedding_req: EmbeddingReq) -> EmbeddingRes:
        try:
            log.debug("Starting OpenAI Embedding")
            res: OpenAIObject = await openai.Embedding.acreate(**embedding_req.dict())
            log.debug("Completed OpenAI Embedding")
            resp: EmbeddingRes = EmbeddingRes(**res.to_dict())
            return resp
        except Exception as e:
            log.error(e)
