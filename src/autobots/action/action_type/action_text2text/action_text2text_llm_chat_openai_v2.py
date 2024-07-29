from typing import Type, List

from loguru import logger
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam, \
    ChatCompletionToolParam
from pydantic import ValidationError

from src.autobots.data_model.context import Context
from src.autobots.exception.app_exception import AppException
from src.autobots.llm.tools.tool_factory import ToolFactory
from src.autobots.llm.tools.tools_map import TOOLS_MAP
from src.autobots.action.action.action_doc_model import ActionResult
from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionOutputType, ActionInputType, \
    ActionConfigType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.action.action.common_action_models import TextObj, TextObjs
from src.autobots.conn.openai.openai_chat.chat_model import ChatReq, Role
from src.autobots.conn.openai.openai_client import get_openai
from src.autobots.user.user_orm_model import UserORM


class ActionText2TextLlmChatOpenai(ActionABC[ChatReq, ChatReq, ChatReq, TextObj, TextObjs]):
    type = ActionType.text2text_llm_chat_openai

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return ChatReq

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return ChatReq

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return ChatReq

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return TextObj

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return TextObjs

    def __init__(self, action_config: ChatReq, user: UserORM | None = None):
        super().__init__(action_config=action_config, user=user)

    @staticmethod
    async def update_config_with_prev_results(
            curr_config: ChatReq,
            prev_results: List[ActionResult] | None = None
    ) -> ChatReq:
        if not prev_results:
            return curr_config

        for prev_result in prev_results:
            action_input: TextObj = ActionText2TextLlmChatOpenai.get_input_type().model_validate(prev_result.input)
            action_output: TextObjs = ActionText2TextLlmChatOpenai.get_output_type().model_validate(prev_result.output)
            config_message_1 = [ChatCompletionUserMessageParam(role="user", content=action_input.text)]
            config_messages_2 = [
                ChatCompletionAssistantMessageParam(role="assistant", content=prev_output_text_obj.text) for
                prev_output_text_obj in action_output.texts]

            curr_config.messages = curr_config.messages + config_message_1 + config_messages_2
        return curr_config

    async def run_action(self, ctx: Context, action_input: TextObj) -> TextObjs:
        text_objs = TextObjs(texts=[])
        try:
            tool_defs = await ActionText2TextLlmChatOpenai.replace_action_tools_with_tools_defs(self.action_config)
            self.action_config.tools = tool_defs

            if action_input and action_input.text != "":
                # message = Message(role=Role.user.value, content=action_input.text)
                message = ChatCompletionUserMessageParam(role=Role.user.value, content=action_input.text)
                self.action_config.messages = self.action_config.messages + [message]
            chat_res = await get_openai().openai_chat.chat(ctx=ctx, chat_req=self.action_config, user=self.user)
            # remove input message from Config messages #TODO: dont remove
            # self.action_config.messages.pop()
            if not chat_res:
                return text_objs
            # resp = Message.model_validate(chat_res.choices[0].message)
            for choice in chat_res.choices:
                text_objs.texts.append(TextObj(text=choice.message.content))
            return text_objs
        except ValidationError as e:
            logger.error(str(e))

    async def run_tool(self, action_config: ChatReq, ctx: Context) -> TextObjs | Exception:
        text_objs = TextObjs(texts=[])
        try:
            tool_defs = await ActionText2TextLlmChatOpenai.replace_action_tools_with_tools_defs(action_config)
            action_config.tools = tool_defs
            chat_res = await get_openai().openai_chat.chat(ctx=ctx, chat_req=action_config, user=self.user)
            if not chat_res:
                raise AppException(detail="Cannot run LLM", http_status=500)
            for choice in chat_res.choices:
                text_objs.texts.append(TextObj(text=choice.message.content))
            return text_objs
        except Exception as e:
            logger.error(str(e))
            return e

    @staticmethod
    async def replace_action_tools_with_tools_defs(action_config: ChatReq) -> List[ChatCompletionToolParam] | None:
        tool_defs = []
        if action_config.tools:
            action_tools = []
            for action_tool in action_config.tools:
                if isinstance(action_tool, str):
                    if action_tool in TOOLS_MAP:
                        action_tools.append(action_tool)
                if isinstance(action_tool, dict):
                    tool_defs.append(action_tool)
            new_tool_defs = await ToolFactory.get_chat_completion_tool_param(action_tools)
            if new_tool_defs:
                tool_defs += new_tool_defs
            if len(tool_defs) == 0:
                return None
            return tool_defs
