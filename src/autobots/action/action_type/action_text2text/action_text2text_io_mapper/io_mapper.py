from typing import Dict, Any

from pydantic import BaseModel

from src.autobots.action.action.common_action_models import TextObj, TextObjs
from src.autobots.action.action_type.action_text2text.action_text2text_io_mapper.action_map_copy import (
    ACTION_MAP_COPY,
)
from src.autobots.action.action_type.action_text2text.action_text2text_llm_chat_with_vector_search_openai import (
    ActionCreateText2TextLlmChatWithVectorSearchOpenaiConfig,
    ActionText2TextLlmChatWithVectorSearchOpenai,
)
from src.autobots.action.action_type.action_types import ActionType


class IOMapperConfig(BaseModel):
    chat_config: ActionCreateText2TextLlmChatWithVectorSearchOpenaiConfig
    prev_action_output: Dict[str, Any]
    prev_action_type: ActionType | None = None
    next_action_type: ActionType


class IOMapper:
    async def map_to_output(self, mapper_config: IOMapperConfig) -> TextObjs | None:
        instruction = self._build_instruction(mapper_config)

        # mapper_config.chat_config.chat_req.messages.append({
        #     "role": "user", "content": instruction
        # })
        chat_action = ActionText2TextLlmChatWithVectorSearchOpenai(
            mapper_config.chat_config
        )
        action_input = TextObj(text=instruction)
        resp = await chat_action.run_action(action_input)
        return resp

    async def _build_instruction(self, mapper_config: IOMapperConfig) -> str:
        instruction_start = "\nGiven the Input, the input json schema and the output json schema, create a json of the output.\n"
        input_context = await self._build_data_context(mapper_config)
        mapping_context = await self._build_mapping_context(mapper_config)
        instruction_end = "\nNote: only respond with output json.\n"
        instruction = (
            f"{instruction_start}{input_context}{mapping_context}{instruction_end}"
        )
        return instruction

    async def _build_data_context(self, mapper_config: IOMapperConfig) -> str:
        context = f"Input data is:\n{mapper_config.prev_action_output}"
        return context

    async def _build_mapping_context(self, mapper_config: IOMapperConfig) -> str:
        context = ""
        if mapper_config.input_action:
            # USING ACTION_MAP_COPY TO SAVE FROM CIRCULAR IMPORT
            input_action_output_data_type = (
                ACTION_MAP_COPY.get(mapper_config.prev_action_type)
                .get_output_type()
                .model_json_schema()
            )
            context = (
                context + f"\nInput datatype is:\n{input_action_output_data_type}\n"
            )
        if mapper_config.output_action:
            # USING ACTION_MAP_COPY TO SAVE FROM CIRCULAR IMPORT
            output_action_data_type = (
                ACTION_MAP_COPY.get(mapper_config.next_action_type)
                .get_input_type()
                .model_json_schema()
            )
            context = context + f"\nOutput datatype is:\n{output_action_data_type}"
        return context
