from typing import Type, List, Dict, Any

from loguru import logger
import httpx
from httpx import URL

from pydantic import ValidationError
# from anthropic.types import Message
from src.autobots.conn.claude.chat_model import Message
from src.autobots.data_model.context import Context
from src.autobots.llm.tools.tool_factory_claude import ToolFactoryClaude
from src.autobots.llm.tools.tools_map import TOOLS_MAP
from src.autobots.action.action.action_doc_model import ActionResult
from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionOutputType, ActionInputType, ActionConfigType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.action.action.common_action_models import MultiObj, MultiObjs, TextObj
from src.autobots.conn.claude.chat_model import ChatReqClaude, Role
from src.autobots.conn.claude.claude_client import get_claude
import base64
from src.autobots.conn.aws.aws_s3 import get_s3
from src.autobots.core.utils import gen_uuid
from src.autobots.user.user_orm_model import UserORM

prefix = "test_"+str(gen_uuid())
s3 = get_s3(object_prefix=prefix)

class ActionText2TextLlmChatclaude(ActionABC[ChatReqClaude, ChatReqClaude, ChatReqClaude, MultiObj, MultiObjs]):
    type = ActionType.text2text_llm_chat_claude

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return ChatReqClaude

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return ChatReqClaude

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return ChatReqClaude

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return MultiObj

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return MultiObjs

    def __init__(self, action_config: ChatReqClaude, user: UserORM | None = None):
        super().__init__(action_config=action_config, user=user)

    # @staticmethod
    # async def update_config_with_prev_IO(
    #         curr_config: ChatReqClaude,
    #         prev_input: MultiObj | None = None,
    #         prev_output: MultiObjs | None = None,
    # ) -> ChatReqClaude:
    #     #     Message,
    #     #     Message,
    #     if not prev_input or not prev_output or prev_input.text == "" or len(prev_output.texts) == 0:
    #         return curr_config
    #     updated_messages = (
    #             curr_config.messages +
    #             [Message(role="user", content=prev_input.text)] +
    #             [Message(role="assistant", content=prev_output_text_obj.text) for
    #              prev_output_text_obj in prev_output.texts]
    #     )
    #     curr_config.messages = updated_messages
    #     return curr_config

    @staticmethod
    async def update_config_with_prev_results(
            curr_config: ChatReqClaude,
            prev_results: List[ActionResult] | None = None
    ) -> ChatReqClaude:
        if not prev_results:
            return curr_config

        for prev_result in prev_results:
            action_input: MultiObj = ActionText2TextLlmChatclaude.get_input_type().model_validate(prev_result.input)
            action_output: MultiObjs = ActionText2TextLlmChatclaude.get_output_type().model_validate(prev_result.output)
            config_message_1 = [Message(role="user", content=action_input.text)]
            config_messages_2 = [
                Message(role="assistant", content=prev_output_text_obj.text) for
                prev_output_text_obj in action_output.texts]

            curr_config.messages = curr_config.messages + config_message_1 + config_messages_2
        return curr_config

    async def run_action(self, ctx: Context, action_input: MultiObj) -> MultiObjs:
        text_objs = MultiObjs(texts=[])
        try:
            tool_defs = await self.replace_action_tools_with_tools_defs()
            self.action_config.tools = tool_defs

            if action_input and action_input.text != "":
                # message = Message(role=Role.user.value, content=action_input.text)
                # message = Message(role=Role.user.value, content=action_input.text)
                content=[]
                for filename in action_input.urls:
                        if filename.startswith('s3://') :  
                            download_file_path = f'/tmp/{gen_uuid()}'
                            with open(download_file_path, "wb") as file:
                                is_downloaded = await s3.download_fileobj(filename, file)
                                assert is_downloaded
                            with open(download_file_path, "rb") as image_file:
                                binary_data = image_file.read()
                                base_64_encoded_data = base64.b64encode(binary_data)
                        else:
                            response= httpx.Client().get(url=URL(filename))
                            base_64_encoded_data= base64.b64encode(response.content)
                        base64_string = base_64_encoded_data.decode('utf-8')
                        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64_string}})
                if isinstance(self.action_config.messages[0].content, str):
                    content.append({"type": "text", "text":self.action_config.messages[0].content + "\n"+action_input.text})
                else:
                    content.append({"type": "text", "text":self.action_config.messages[0].content[-1]["text"] + "\n"+action_input.text})
                self.action_config.messages = [Message(role=Role.user.value, content = content)]
                
            chat_res = await get_claude().claude_chat.chat(ctx=ctx, chat_req=self.action_config)
            # remove input message from Config messages #TODO: dont remove
            # self.action_config.messages.pop()
            if not chat_res:
                return text_objs
            # resp = Message.model_validate(chat_res.choices[0].message)
            for choice in chat_res.content:
                text_objs.texts.append(TextObj(text=choice.text))
            return text_objs
        except ValidationError as e:
            logger.error(str(e))

    async def replace_action_tools_with_tools_defs(self) -> List[Dict[str, Any]] | None:
        action_tools = []
        if self.action_config.tools:
            for action_tool in self.action_config.tools:
                if isinstance(action_tool, str):
                    if action_tool in TOOLS_MAP:
                        action_tools.append(action_tool)
            tool_defs = await ToolFactoryClaude.get_tool_definations(action_tools)
            return tool_defs

