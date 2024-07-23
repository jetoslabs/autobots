from typing import List

from loguru import logger
from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionToolMessageParam, \
    ChatCompletionMessageParam, ChatCompletionMessage
from retry import retry

from src.autobots.conn.openai.openai_chat.chat_model import ChatReq
from src.autobots.core.logging.app_code import AppCode
from src.autobots.core.logging.log_binder import LogBinder
from src.autobots.llm.tools.tool_factory import ToolFactory
from src.autobots.user.user_orm_model import UserORM


class OpenaiChat:

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

    @retry(exceptions=Exception, tries=3, delay=30)
    async def chat(
            self, chat_req: ChatReq, user: UserORM | None = None
    ) -> ChatCompletion | AsyncStream[ChatCompletionChunk] | None:
        # model vision is resulting in error because of these 6 extra params
        # if chat_req.model.__contains__("-vision-"):
        #     chat_req.logit_bias = None
        #     chat_req.logprobs = None
        #     chat_req.response_format = None
        #     chat_req.tool_choice = None
        #     chat_req.tools = None
        #     chat_req.top_logprobs = None
        #     logger.warning(
        #         f"Openai Chat model {chat_req.model} does not accept some params, removing them before calling Openai API")
        try:
            logger.trace("Starting OpenAI Chat, try: 1")
            # res: ChatCompletion = await self.client.chat.completions.create(**chat_req.model_dump(exclude_none=True))
            res: ChatCompletion = await self.chat_loop(chat_req, user)
            logger.trace("Completed OpenAI Chat")
            if isinstance(res, AsyncStream):
                return self.yield_chat_chunks(res)
            else:
                return res
        except Exception as e:
            logger.error(str(e))
            raise

    async def chat_loop(self, chat_req: ChatReq, user: UserORM | None = None) -> ChatCompletion | AsyncStream[ChatCompletionChunk]:
        # is_continue: bool = True
        while True:
            chat_completion: ChatCompletion = await self.client.chat.completions.create(
                **chat_req.model_dump(exclude_none=True)
            )
            if isinstance(chat_completion, AsyncStream):
                return chat_completion
            choice = chat_completion.choices[-1]
            chat_req.messages.append(choice.message)
            if choice.finish_reason == "stop":
                return chat_completion
            elif choice.finish_reason == "tool_calls":
                messages = await self.run_tools(choice, user)
                chat_req.messages = chat_req.messages + messages

    async def yield_chat_chunks(self, chat_res: AsyncStream[ChatCompletionChunk]) -> ChatCompletionChunk | None:
        try:
            async for part in chat_res:
                yield part
        except Exception as e:
            logger.error(str(e))

    async def run_tools(self, choice, user: UserORM | None = None) -> List[ChatCompletionMessageParam | ChatCompletionMessage]:
        messages = []
        for tool_call in choice.message.tool_calls:
            tool_call_id = tool_call.id
            tool_name = tool_call.function.name
            tool_args = tool_call.function.arguments
            try:
                # run tool
                tool_output_str: str = await ToolFactory(user).run_tool(tool_name, tool_args)
                logger.bind(
                    **LogBinder()
                    .with_app_code(AppCode.ACTION)
                    .with_kwargs(tool=tool_name, tool_output=tool_output_str)
                    .get_bind_dict()
                ).debug(f"Ran tool in {OpenaiChat.__name__}")
                # add tool call output to Messages
                tool_output_message = ChatCompletionToolMessageParam(role="tool", content=tool_output_str,
                                                                     tool_call_id=tool_call_id)
                messages.append(tool_output_message)
                # await self.chat_loop(chat_req)
            except Exception as e:
                logger.bind(
                    **LogBinder()
                    .with_app_code(AppCode.ACTION)
                    .with_kwargs(tool=tool_name, tool_error=str(e))
                    .get_bind_dict()
                ).error(str(e))
                # add tool call error to Messages
                tool_error_message = ChatCompletionToolMessageParam(role="tool", content=str(e),
                                                                    tool_call_id=tool_call_id)
                messages.append(tool_error_message)
        return messages
