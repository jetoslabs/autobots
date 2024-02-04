from loguru import logger
from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from retry import retry

from src.autobots.conn.openai.openai_chat.chat_model import ChatReq


class OpenaiChat:

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

    @retry(exceptions=Exception, tries=3, delay=30)
    async def chat(self, chat_req: ChatReq) -> ChatCompletion | AsyncStream[ChatCompletionChunk] | None:
        # model vision is resulting in error because of these 6 extra params
        if chat_req.model.__contains__("-vision-"):
            chat_req.logit_bias = None
            chat_req.logprobs = None
            chat_req.response_format = None
            chat_req.tool_choice = None
            chat_req.tools = None
            chat_req.top_logprobs = None
            logger.warning(f"Openai Chat model {chat_req.model} does not accept some params, removing them before calling Openai API")
        try:
            logger.trace("Starting OpenAI Chat, try: 1")
            res: ChatCompletion = await self.client.chat.completions.create(**chat_req.model_dump(exclude_none=True))
            logger.trace("Completed OpenAI Chat")
            if isinstance(res, AsyncStream):
                return self.yield_chat_chunks(res)
            else:
                return res
        except Exception as e:
            logger.error(str(e))
            raise

    async def yield_chat_chunks(self, chat_res: AsyncStream[ChatCompletionChunk]) -> ChatCompletionChunk | None:
        try:
            async for part in chat_res:
                yield part
        except Exception as e:
            logger.error(str(e))
