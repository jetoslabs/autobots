import json
from typing import List

from loguru import logger
from openai.types.beta import FunctionToolParam
from openai.types.chat import ChatCompletionToolParam

from src.autobots.conn.openai.openai_function_definition_gen import OpenAIFunctionDefinitionGen
from src.autobots.data_model.context import Context
from src.autobots.llm.tools.tools_map import TOOLS_MAP
from src.autobots.user.user_orm_model import UserORM


class ToolFactory:

    def __init__(self, user: UserORM | None = None):
        self.user = user

    @staticmethod
    async def get_tools() -> List[str]:
        tools = []
        for tool in TOOLS_MAP.keys():
            tools += [tool]
        return tools

    @staticmethod
    async def get_function_tool_param(tool_names: List[str]) -> List[FunctionToolParam] | None:
        func_defs = []
        for tool_name in tool_names:
            try:
                action = TOOLS_MAP.get(tool_name)
                func_def = await OpenAIFunctionDefinitionGen.get_function_tool_param(
                    action.run_tool, action.get_description()
                )
                func_def.get("function")["name"] = tool_name
                func_defs.append(func_def)
            except Exception as e:
                logger.error(str(e))
        return func_defs if len(func_defs) > 0 else None

    @staticmethod
    async def get_chat_completion_tool_param(tool_names: List[str]) -> List[ChatCompletionToolParam] | None:
        func_defs = []
        for tool_name in tool_names:
            try:
                action = TOOLS_MAP.get(tool_name)
                func_def = await OpenAIFunctionDefinitionGen.get_chat_completion_tool_param(
                    action.run_tool, action.get_description()
                )
                func_def.get("function")["name"] = tool_name
                func_defs.append(func_def)
            except Exception as e:
                logger.bind(tool_name=tool_name).error(str(e))
        return func_defs if len(func_defs) > 0 else None

    async def run_tool(self, ctx: Context, tool_name: str, tool_args) -> str:
        # tool_args is 1st param of tool_name
        tool_output = ""
        try:
            action_type = TOOLS_MAP.get(tool_name)
            config = action_type.get_config_type().model_validate(json.loads(tool_args))
            action = action_type(config, self.user)
            output = await action.run_tool(action_config=config, ctx=ctx)
            output_str = ""
            match output:
                case Exception():
                    output_str = str(output)
                case _:
                    output_str = output.model_dump_json(exclude_none=True)  #json.dumps(output.model_dump())
            tool_output = output_str
            logger.bind(ctx=ctx, tool_name=tool_name, tool_args=tool_args, tool_output=tool_output).info(f"Ran tool: {tool_name}")
        except Exception as e:
            tool_output = str(e)
            logger.bind(ctx=ctx, tool_name=tool_name, tool_args=tool_args, tool_output=tool_output).error(f"Error in run tool{str(e)}")
        finally:
            return tool_output
