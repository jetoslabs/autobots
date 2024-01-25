import time

from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from retry import retry

from src.autobots.conn.openai.openai_chat.chat_model import ChatReq
from src.autobots.core.logging.log import Log


class OpenaiChat:

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

    @retry(Exception, tries=3, delay=30)
    async def chat(self, chat_req: ChatReq) -> ChatCompletion | AsyncStream[ChatCompletionChunk] | None:
        try:
            Log.trace("Starting OpenAI Chat, try: 1")
            res: ChatCompletion = await self.client.chat.completions.create(**chat_req.model_dump())
            Log.trace("Completed OpenAI Chat")
            if isinstance(res, AsyncStream):
                return self.yield_chat_chunks(res)
            else:
                return res
        except Exception as e:
            Log.error(str(e))
            raise

    async def yield_chat_chunks(self, chat_res: AsyncStream[ChatCompletionChunk]) -> ChatCompletionChunk | None:
        try:
            async for part in chat_res:
                yield part
        except Exception as e:
            Log.error(str(e))
