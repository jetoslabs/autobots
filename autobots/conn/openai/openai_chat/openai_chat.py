import time

from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from autobots.conn.openai.openai_chat.chat_model import ChatReq
from autobots.core.log import log


class OpenaiChat:

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

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
