from typing import Optional, Type, List

from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam
from pydantic import BaseModel

from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionOutputType, ActionInputType, ActionConfigType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action.action_doc_model import ActionCreate, ActionResult
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.action.action.common_action_models import TextObj, TextObjs
from src.autobots.conn.aws.s3 import get_s3
from src.autobots.conn.openai.openai_chat.chat_model import ChatReq, Role
from src.autobots.conn.openai.openai_client import get_openai
from src.autobots.conn.pinecone.pinecone import get_pinecone
from src.autobots.conn.unstructured_io.unstructured_io import get_unstructured_io
from src.autobots.data_model.context import Context
from src.autobots.datastore.datastore import Datastore
from src.autobots.user.user_orm_model import UserORM


class ActionCreateText2TextLlmChatWithVectorSearchOpenaiConfig(BaseModel):
    datastore_id: str
    chat_req: ChatReq
    input: Optional[TextObj] = None
    output: Optional[TextObjs] = None


class ActionCreateText2TextLlmChatWithVectorSearchOpenai(ActionCreate):
    type: ActionType = ActionType.text2text_llm_chat_with_vector_search_openai
    config: ActionCreateText2TextLlmChatWithVectorSearchOpenaiConfig


class ActionText2TextLlmChatWithVectorSearchOpenai(
    ActionABC[
        ActionCreateText2TextLlmChatWithVectorSearchOpenaiConfig,
        ActionCreateText2TextLlmChatWithVectorSearchOpenaiConfig,
        ActionCreateText2TextLlmChatWithVectorSearchOpenaiConfig,
        TextObj,
        TextObjs
    ]
):
    """
    Vector search and add it to chat prompt as context
    """
    type = ActionType.text2text_llm_chat_with_vector_search_openai

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return ActionCreateText2TextLlmChatWithVectorSearchOpenaiConfig

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return ActionCreateText2TextLlmChatWithVectorSearchOpenaiConfig

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return ActionCreateText2TextLlmChatWithVectorSearchOpenaiConfig

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return TextObj

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return TextObjs

    def __init__(self, action_config: ActionCreateText2TextLlmChatWithVectorSearchOpenaiConfig, user: UserORM | None = None):
        super().__init__(action_config=action_config, user=user)
        self.datastore = Datastore(
            s3=get_s3(),
            pinecone=get_pinecone(),
            unstructured=get_unstructured_io()
        ).hydrate(
            datastore_id=action_config.datastore_id
        )

    # @staticmethod
    # async def update_config_with_prev_IO(
    #         curr_config: ActionCreateText2TextLlmChatWithVectorSearchOpenaiConfig,
    #         prev_input: TextObj | None = None,
    #         prev_output: TextObjs | None = None,
    # ) -> ActionCreateText2TextLlmChatWithVectorSearchOpenaiConfig:
    #     #     ChatCompletionUserMessageParam,
    #     #     ChatCompletionAssistantMessageParam,
    #     if not prev_input or not prev_output or prev_input.text == "" or len(prev_output.texts) == 0 :
    #         return curr_config
    #     updated_messages = (
    #             curr_config.chat_req.messages +
    #             [ChatCompletionUserMessageParam(role="user", content=prev_input.text)] +
    #             [ChatCompletionAssistantMessageParam(role="assistant", content=prev_output_text_obj.text) for prev_output_text_obj in prev_output.texts]
    #     )
    #     curr_config.chat_req.messages = updated_messages
    #     return curr_config

    @staticmethod
    async def update_config_with_prev_results(
            curr_config: ActionCreateText2TextLlmChatWithVectorSearchOpenaiConfig,
            prev_results: List[ActionResult] | None = None
    ) -> ActionCreateText2TextLlmChatWithVectorSearchOpenaiConfig:
        if not prev_results:
            return curr_config

        for prev_result in prev_results:
            action_input: TextObj = ActionText2TextLlmChatWithVectorSearchOpenai.get_input_type().model_validate(prev_result.input)
            action_output: TextObjs = ActionText2TextLlmChatWithVectorSearchOpenai.get_output_type().model_validate(prev_result.output)
            config_message_1 = [ChatCompletionUserMessageParam(role="user", content=action_input.text)]
            config_messages_2 = [
                ChatCompletionAssistantMessageParam(role="assistant", content=prev_output_text_obj.text) for
                prev_output_text_obj in action_output.texts]

            curr_config.chat_req.messages = curr_config.chat_req.messages + config_message_1 + config_messages_2
        return curr_config

    async def run_action(self, ctx: Context, action_input: TextObj) -> TextObjs | None:
        # text_objs = TextObjs(texts=[])
        # vector search
        search_results = await self.datastore.search(action_input.text, top_k=3)
        if len(search_results) == 0:
            return None
        context = "Only use relevant context to give response. If the context is insufficient say \"Cannot answer from given context\"\nContext: \n"
        for result in search_results:
            context = f"{context}{result}\n"
        # LM chat
        message = ChatCompletionUserMessageParam(role=Role.user.value, content=f"{context}Question: {action_input.text}")
        self.action_config.chat_req.messages = self.action_config.chat_req.messages + [message]
        self.action_config.input = action_input
        chat_res = await get_openai().openai_chat.chat(ctx=ctx, chat_req=self.action_config.chat_req)
        action_results = TextObjs()
        for choice in chat_res.choices:
            action_results.texts.append(TextObj(text=choice.message.content))
        return action_results
