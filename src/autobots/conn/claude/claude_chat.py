from loguru import logger
from retry import retry
from anthropic import AsyncAnthropic, AsyncStream
from anthropic.types import (
    Message, MessageParam, MessageStreamEvent
)

from src.autobots.conn.claude.chat_model import ChatReqClaude
from src.autobots.core.logging.app_code import AppCode
from src.autobots.core.logging.log_binder import LogBinder
from src.autobots.llm.tools.tool_factory_claude import ToolFactoryClaude


class AnthropicChat:

    def __init__(self, anthropic_client: AsyncAnthropic):
        self.client = anthropic_client

    @retry(exceptions=Exception, tries=3, delay=30)
    async def chat(self, chat_req: ChatReqClaude) -> Message | AsyncStream[MessageStreamEvent] | None:
        try:
            logger.trace("Starting Anthropic Chat, try: 1")
            res: Message = await self.chat_loop(chat_req)
            logger.trace("Completed Anthropic Chat")
            if isinstance(res, AsyncStream):
                return self.yield_chat_chunks(res)
            else:
                return res
        except Exception as e:
            logger.error(str(e))
            raise

    async def chat_loop(self, chat_req: ChatReqClaude) -> Message | AsyncStream[MessageStreamEvent]:
        while True:
            logger.info(chat_req.model_dump(exclude_none=True))
            chat_completion: Message = await self.client.messages.create(
                **chat_req.model_dump(exclude_none=True)
            )
            if isinstance(chat_completion, AsyncStream):
                return chat_completion
                 # Accessing the tool_use content
            # print(chat_completion)
            if chat_completion.stop_reason == "end_turn":
                return chat_completion
            elif chat_completion.stop_reason == "tool_use":
                try:
                    # TODO:change calls here
                    tool_use_info = chat_completion.content[-1]
                    name = tool_use_info.name
                    args = tool_use_info.input
                    # add tool call to Messages
                    tool_message = MessageParam(
                        role="assistant", content="Tool_call " + name
                    )
                    chat_req.messages.append(tool_message)
                    # run tool
                    tool_output_str: str = await ToolFactoryClaude.run_tool(name, args)
                    tool_output_message = MessageParam(role="user", content=tool_output_str)
                    logger.bind(
                        **LogBinder()
                        .with_app_code(AppCode.ACTION)
                        .with_kwargs(tool=name, tool_output=tool_output_str)
                        .get_bind_dict()
                    ).debug(f"Ran tool in {AnthropicChat.__name__}")
                    chat_req.messages.append(tool_output_message)
                except Exception as e:
                    logger.error(str(e))

    async def yield_chat_chunks(self, chat_res: AsyncStream[MessageStreamEvent]) -> MessageStreamEvent | None: # type: ignore
        try:
            async for part in chat_res:
                yield part
        except Exception as e:
            logger.error(str(e))
