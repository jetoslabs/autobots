from loguru import logger
from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionAssistantMessageParam, \
    ChatCompletionUserMessageParam
from retry import retry

from src.autobots.conn.openai.openai_chat.chat_model import ChatReq
from src.autobots.llm.tools.tool_factory import ToolFactory


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
            # res: ChatCompletion = await self.client.chat.completions.create(**chat_req.model_dump(exclude_none=True))
            res: ChatCompletion = await self.chat_loop(chat_req)
            logger.trace("Completed OpenAI Chat")
            if isinstance(res, AsyncStream):
                return self.yield_chat_chunks(res)
            else:
                return res
        except Exception as e:
            logger.error(str(e))
            raise

    async def chat_loop(self, chat_req: ChatReq) -> ChatCompletion:
        # is_continue: bool = True
        while True:
            chat_completion: ChatCompletion = await self.client.chat.completions.create(
                **chat_req.model_dump(exclude_none=True)
            )
            choice = chat_completion.choices[-1]
            if choice.finish_reason == "stop":
                return chat_completion
            elif choice.finish_reason == "tool_calls":
                try:
                    name = choice.message.tool_calls[0].function.name
                    args = choice.message.tool_calls[0].function.arguments
                    # add tool call to Messages
                    tool_message = ChatCompletionAssistantMessageParam(
                        role="assistant", content="Tool_call " + choice.message.tool_calls[0].function.name
                    )
                    chat_req.messages.append(tool_message)
                    # run tool
                    tool_output_str: str = await ToolFactory.run_tool(name, args)
                    tool_output_message = ChatCompletionUserMessageParam(role="user", content=tool_output_str)
                    chat_req.messages.append(tool_output_message)
                    # await self.chat_loop(chat_req)
                except Exception as e:
                    logger.error(str(e))

    async def yield_chat_chunks(self, chat_res: AsyncStream[ChatCompletionChunk]) -> ChatCompletionChunk | None:
        try:
            async for part in chat_res:
                yield part
        except Exception as e:
            logger.error(str(e))
