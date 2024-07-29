import time
from typing import Type, List, Iterable

from loguru import logger
from openai.types.beta import Assistant, AssistantToolParam
from openai.types.beta.threads import Message, ImageFileContentBlock, TextContentBlock

from src.autobots.action.action.common_action_models import AssistantObj, TextObj, TextObjs
from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionInputType, ActionOutputType, ActionConfigType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_multimodal.action_multimodal_assistant_openai.assistant_openai_model import \
    AssistantOpenaiConfigCreate, AssistantOpenaiConfigUpdate, AssistantOpenaiConfig
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.openai.openai_assistants.assistant_model import AssistantDelete, AssistantUpdate
from src.autobots.conn.openai.openai_assistants.openai_thread_messages.openai_thread_messages_model import \
    ThreadMessagesCreate, ThreadMessageList
from src.autobots.conn.openai.openai_assistants.openai_thread_runs.openai_thread_runs_model import ThreadRunCreate, ThreadRunCreateAndRun, \
    ThreadRunRetrieve, ThreadRunSubmitToolOutputs
from src.autobots.conn.openai.openai_assistants.openai_threads.openai_threads_model import ThreadCreate
from src.autobots.conn.openai.openai_client import get_openai
from src.autobots.conn.openai.openai_files.openai_files_model import FileContent
from src.autobots.core.logging.log_binder import LogBinder
from src.autobots.data_model.context import Context
from src.autobots.llm.tools.tool_factory import ToolFactory
from src.autobots.llm.tools.tools_map import TOOLS_MAP
from src.autobots.user.user_orm_model import UserORM


class ActionMultimodalAssistantOpenai(
    ActionABC[AssistantOpenaiConfigCreate, AssistantOpenaiConfigUpdate, AssistantOpenaiConfig, TextObj, TextObjs]
):
    type = ActionType.multimodal_assistant_openai

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return AssistantOpenaiConfigCreate

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return AssistantOpenaiConfigUpdate

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return AssistantOpenaiConfig

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return TextObj

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return TextObjs

    @staticmethod
    async def create_config(config_create: AssistantOpenaiConfigCreate) -> AssistantOpenaiConfig:
        assistant_tools = await ActionMultimodalAssistantOpenai.replace_action_tools_with_tools_defs(config_create.tools)
        config_create.tools = assistant_tools

        assistant_client = get_openai().openai_assistants
        # create assistant
        assistant: Assistant = await assistant_client.create(config_create)
        return AssistantOpenaiConfig.model_validate(assistant.model_dump())

    @staticmethod
    async def update_config(config: AssistantOpenaiConfig,
                            config_update: AssistantOpenaiConfigUpdate) -> AssistantOpenaiConfig:
        assistant_tools = await ActionMultimodalAssistantOpenai.replace_action_tools_with_tools_defs(config_update.tools)
        config_update.tools = assistant_tools

        assistant_client = get_openai().openai_assistants
        assistant_update = AssistantUpdate(assistant_id=config.id, **config_update.model_dump(exclude_none=True))
        assistant: Assistant = await assistant_client.update(assistant_update)
        return AssistantOpenaiConfig.model_validate(assistant.model_dump())

    @staticmethod
    async def delete_config(config: AssistantOpenaiConfig) -> AssistantOpenaiConfig:
        assistant_client = get_openai().openai_assistants
        # delete assistant
        assistant_delete = AssistantDelete(assistant_id=config.id)
        await assistant_client.delete(assistant_delete)
        return config

    def __init__(self, action_config: AssistantOpenaiConfig, user: UserORM | None = None):
        super().__init__(action_config=action_config, user=user)

    async def run_action(self, ctx: Context, action_input: AssistantObj) -> TextObjs:
        assistant_client = get_openai().openai_assistants
        assistant = self.action_config
        try:
            # create thread
            thread_create = ThreadCreate()
            thread = await assistant_client.threads.create(thread_create)
            # add message
            thread_message_create_1 = ThreadMessagesCreate(thread_id=thread.id,
                                                           content=action_input.text)
            thread_message = await assistant_client.threads.messages.create(thread_message_create_1)  # noqa F841
            # run thread
            tools = [tool.model_dump(exclude_none=True) for tool in assistant.tools + action_input.tools] # TODO: add description to func definition
            # tool_resources = [resource.model_dump(exclude_none=True) for resource in action_input.tool_resources]
            thread_run_create = ThreadRunCreate(thread_id=thread.id, assistant_id=assistant.id,
                                                instructions=assistant.instructions, tools=tools)
            run = await assistant_client.threads.runs.create(thread_run_create)
            # TODO: store thread_id and run_id for re-run in Output
            # get run status - loop until status completed
            # The status of the run, which can be either:
            #   exit criteria - completed, cancelled, failed, expired
            #   wait criteria - queued, in_progress, cancelling, incomplete
            #   action criteria - requires_action
            while True:
                thread_run_retrieve = ThreadRunRetrieve(thread_id=run.thread_id, run_id=run.id)
                run = await assistant_client.threads.runs.retrieve(thread_run_retrieve)
                if run.status in ["completed", "cancelled", "failed", "expired"]:
                    break
                elif run.status in ["queued", "in_progress", "cancelling", "incomplete"]:
                    time.sleep(10)
                elif run.status == "requires_action":
                    tool_outputs = []
                    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                        name = tool_call.function.name
                        args = tool_call.function.arguments
                        # run tool
                        tool_output_str: str = await ToolFactory(self.user).run_tool(ctx, name, args)
                        tool_output = {
                            "output": tool_output_str,
                            "tool_call_id": tool_call.id
                        }
                        tool_outputs.append(tool_output)
                    thread_run_submit_tool_outputs = ThreadRunSubmitToolOutputs(
                        thread_id=run.thread_id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
                    run = await assistant_client.threads.runs.submit_tool_outputs(thread_run_submit_tool_outputs)
                    # run_status = run.status

            # get list of messages
            # if run.status != "completed":
            #     raise Exception(f"Assistant run status: {run.status}")
            thread_message_list = ThreadMessageList(thread_id=run.thread_id)
            messages = await assistant_client.threads.messages.list(thread_message_list)
            # last generated message is on the top
            message: Message = messages.data[0]
            # create return object
            texts: List[TextObj] = []
            if message.attachments is not None and len(message.attachments) > 0:
                openai_files_client = get_openai().openai_files
                for attachment in message.attachments:
                    logger.bind(**LogBinder().with_kwargs(file_id=attachment.file_id).get_bind_dict()).debug("Reading OpenAI file")
                    file_id = attachment.file_id
                    binary_res = await openai_files_client.retrieve_content(file_content=FileContent(file_id=file_id))
                    binary_content = binary_res.content
                    content = bytes.decode(binary_content)
                    text_obj = TextObj(text=content)
                    texts.append(text_obj)
            else:
                for content in message.content:
                    if isinstance(content, ImageFileContentBlock):
                        pass  # TODO handle image file
                    elif isinstance(content, TextContentBlock):
                        text_obj = TextObj(text=content.text.value)
                        texts.append(text_obj)
            return TextObjs(texts=texts)
        except Exception as e:
            logger.error(str(e))
            raise e

    @staticmethod
    async def replace_action_tools_with_tools_defs(
            tools: Iterable[AssistantToolParam] | List[str] | None = None
    ) -> Iterable[AssistantToolParam] | None:
        function_tools = []
        already_assistant_tools = []
        if tools:
            for action_tool in tools:
                if isinstance(action_tool, str):
                    if action_tool in TOOLS_MAP:
                        function_tools.append(action_tool)
                if isinstance(action_tool, dict):
                    already_assistant_tools.append(action_tool)
        assistant_function_tools = await ToolFactory.get_function_tool_param(function_tools)
        final_list_of_tools = []
        if already_assistant_tools and len(already_assistant_tools) > 0:
            final_list_of_tools += already_assistant_tools
        if assistant_function_tools and len(assistant_function_tools) > 0:
            final_list_of_tools += assistant_function_tools
        return final_list_of_tools if len(final_list_of_tools) > 0 else None
