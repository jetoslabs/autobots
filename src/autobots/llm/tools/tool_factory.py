import json
from typing import List

from loguru import logger
from openai.types.chat import ChatCompletionToolParam

from src.autobots.conn.openai.openai_function_definition_gen import OpenAIFunctionDefinitionGen
from src.autobots.llm.tools.tools_map import TOOLS_MAP


class ToolFactory:

    @staticmethod
    async def get_tools() -> List[str]:
        tools = []
        for tool in TOOLS_MAP.keys():
            tools += [tool]
        return tools

    @staticmethod
    async def get_tool_definations(tool_names: List[str]) -> List[ChatCompletionToolParam] | None:
        func_defs = []
        for tool_name in tool_names:
            try:
                action = TOOLS_MAP.get(tool_name)
                func_def = await OpenAIFunctionDefinitionGen.get_defination(
                    action.create_and_run_action, action.__doc__
                )
                func_def.get("function")["name"] = tool_name
                func_defs.append(func_def)
            except Exception as e:
                logger.error(str(e))
        return func_defs if len(func_defs) > 0 else None

    @staticmethod
    async def run_tool(tool_name, tool_args) -> str:
        tool_output = ""
        try:
            action = TOOLS_MAP.get(tool_name)
            config = action.get_config_type().model_validate(json.loads(tool_args))
            output = await action.create_and_run_action(config)
            output_str = output.model_dump_json(exclude_none=True)  #json.dumps(output.model_dump())
            tool_output = output_str
        except Exception as e:
            logger.error(str(e))
            tool_output = str(e)
        finally:
            return tool_output
