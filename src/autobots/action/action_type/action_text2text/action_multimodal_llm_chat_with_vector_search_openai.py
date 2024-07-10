# from typing import Optional, Type, List
#
# from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam
# from pydantic import BaseModel
# import base64
# import io
# import re
# import uuid
# from PIL import Image
# import os
# from src.autobots.conn.chroma.chroma import Chroma, Document
#
# from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionOutputType, ActionInputType, ActionConfigType, \
# from src.autobots.action.action.action_doc_model import ActionCreate, ActionResult
# from src.autobots.action.action_type.action_types import ActionType
# from src.autobots.action.action.common_action_models import TextObj, TextObjs
# from src.autobots.conn.aws.s3 import get_s3
# from src.autobots.conn.openai.openai_chat.chat_model import ChatReq, Role
# from src.autobots.conn.openai.openai_client import get_openai
# from src.autobots.conn.pinecone.pinecone import get_pinecone
# from src.autobots.conn.unstructured_io.unstructured_io import get_unstructured_io
# from src.autobots.datastore.datastore import Datastore
# from openai import OpenAI
# from src.autobots.core.settings import Settings, SettingsProvider
#
#
# def resize_base64_image(base64_string, size=(128, 128)):
#     """
#     Resize an image encoded as a Base64 string
#     """
#     # Decode the Base64 string
#     img_data = base64.b64decode(base64_string)
#     img = Image.open(io.BytesIO(img_data))
#
#     # Resize the image
#     resized_img = img.resize(size, Image.LANCZOS)
#
#     # Save the resized image to a bytes buffer
#     buffered = io.BytesIO()
#     resized_img.save(buffered, format=img.format)
#
#     # Encode the resized image to Base64
#     return base64.b64encode(buffered.getvalue()).decode("utf-8")
#
# def looks_like_base64(sb):
#     """Check if the string looks like base64"""
#     return re.match("^[A-Za-z0-9+/]+[=]{0,2}$", sb) is not None
#
#
# def is_image_data(b64data):
#     """
#     Check if the base64 data is an image by looking at the start of the data
#     """
#     image_signatures = {
#         b"\xff\xd8\xff": "jpg",
#         b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a": "png",
#         b"\x47\x49\x46\x38": "gif",
#         b"\x52\x49\x46\x46": "webp",
#     }
#     try:
#         header = base64.b64decode(b64data)[:8]  # Decode and get the first 8 bytes
#         for sig, format in image_signatures.items():
#             if header.startswith(sig):
#                 return True
#         return False
#     except Exception:
#         return False
#
# def split_image_text_types(docs):
#     """
#     Split base64-encoded images and texts
#     """
#     b64_images = []
#     texts = []
#     for doc in docs:
#         # Check if the document is of type Document and extract page_content if so
#         if isinstance(doc, Document):
#             doc = doc.page_content
#         if looks_like_base64(doc) and is_image_data(doc):
#             doc = resize_base64_image(doc, size=(1300, 600))
#             b64_images.append(doc)
#         else:
#             texts.append(doc)
#     return {"images": b64_images, "texts": texts}
#
#
# def img_prompt_func(data_dict):
#     """
#     Join the context into a single string
#     """
#     formatted_texts = "\n".join(data_dict["context"]["texts"])
#     messages = []
#
#     # Adding image(s) to the messages if present
#     if data_dict["context"]["images"]:
#         for image in data_dict["context"]["images"]:
#             image_message = {
#                 "type": "image_url",
#                 "image_url": {"url": f"data:image/jpeg;base64,{image}"},
#             }
#             messages.append(image_message)
#
#     # Adding the text for analysis
#     text_message = {
#         "type": "text",
#         "text": (
#             "You are financial analyst tasking with providing investment advice.\n"
#             "You will be given a mixed of text, tables, and image(s) usually of charts or graphs.\n"
#             "Use this information to provide investment advice related to the user question. \n"
#             f"User-provided question: {data_dict['question']}\n\n"
#             "Text and / or tables:\n"
#             f"{formatted_texts}"
#         ),
#     }
#     messages.append(text_message)
#     return messages
#
# class ActionCreateMultiModalLlmChatWithVectorSearchOpenaiConfig(BaseModel):
#     datastore_id: str
#     chat_req: ChatReq
#     input: Optional[TextObj] = None
#     output: Optional[TextObjs] = None
#
#
# class ActionCreateMultiModalLlmChatWithVectorSearchOpenai(ActionCreate):
#     type: ActionType = ActionType.multimodal_llm_chat_with_vector_search_openai
#     config: ActionCreateMultiModalLlmChatWithVectorSearchOpenaiConfig
#
#
# class ActionMultiModalLlmChatWithVectorSearchOpenai(
#     ActionABC[
#         ActionCreateMultiModalLlmChatWithVectorSearchOpenaiConfig,
#         ActionCreateMultiModalLlmChatWithVectorSearchOpenaiConfig,
#         ActionCreateMultiModalLlmChatWithVectorSearchOpenaiConfig,
#         TextObj,
#         TextObjs
#     ]
# ):
#     """
#     Vector search and add it to chat prompt as context
#     """
#     type = ActionType.multimodal_llm_chat_with_vector_search_openai
#
#     @staticmethod
#     def get_config_create_type() -> Type[ActionConfigCreateType]:
#         return ActionCreateMultiModalLlmChatWithVectorSearchOpenaiConfig
#
#     @staticmethod
#     def get_config_update_type() -> Type[ActionConfigUpdateType]:
#         return ActionCreateMultiModalLlmChatWithVectorSearchOpenaiConfig
#
#     @staticmethod
#     def get_config_type() -> Type[ActionConfigType]:
#         return ActionCreateMultiModalLlmChatWithVectorSearchOpenaiConfig
#
#     @staticmethod
#     def get_input_type() -> Type[ActionInputType]:
#         return TextObj
#
#     @staticmethod
#     def get_output_type() -> Type[ActionOutputType]:
#         return TextObjs
#
#     def __init__(self, action_config: ActionCreateMultiModalLlmChatWithVectorSearchOpenaiConfig):
#         super().__init__(action_config)
#         self.datastore = MultiDataStore()
#
#     # @staticmethod
#     # async def update_config_with_prev_IO(
#     #         curr_config: ActionCreateMultiModalLlmChatWithVectorSearchOpenaiConfig,
#     #         prev_input: TextObj | None = None,
#     #         prev_output: TextObjs | None = None,
#     # ) -> ActionCreateMultiModalLlmChatWithVectorSearchOpenaiConfig:
#     #     #     ChatCompletionUserMessageParam,
#     #     #     ChatCompletionAssistantMessageParam,
#     #     if not prev_input or not prev_output or prev_input.text == "" or len(prev_output.texts) == 0 :
#     #         return curr_config
#     #     updated_messages = (
#     #             curr_config.chat_req.messages +
#     #             [ChatCompletionUserMessageParam(role="user", content=prev_input.text)] +
#     #             [ChatCompletionAssistantMessageParam(role="assistant", content=prev_output_text_obj.text) for prev_output_text_obj in prev_output.texts]
#     #     )
#     #     curr_config.chat_req.messages = updated_messages
#     #     return curr_config
#
#     @staticmethod
#     async def update_config_with_prev_results(
#             curr_config: ActionCreateMultiModalLlmChatWithVectorSearchOpenaiConfig,
#             prev_results: List[ActionResult] | None = None
#     ) -> ActionCreateMultiModalLlmChatWithVectorSearchOpenaiConfig:
#         if not prev_results:
#             return curr_config
#
#         for prev_result in prev_results:
#             action_input: TextObj = ActionMultiModalLlmChatWithVectorSearchOpenai.get_input_type().model_validate(prev_result.input)
#             action_output: TextObjs = ActionMultiModalLlmChatWithVectorSearchOpenai.get_output_type().model_validate(prev_result.output)
#             config_message_1 = [ChatCompletionUserMessageParam(role="user", content=action_input.text)]
#             config_messages_2 = [
#                 ChatCompletionAssistantMessageParam(role="assistant", content=prev_output_text_obj.text) for
#                 prev_output_text_obj in action_output.texts]
#
#             curr_config.chat_req.messages = curr_config.chat_req.messages + config_message_1 + config_messages_2
#         return curr_config
#
#     async def run_action(self, action_input: TextObj) -> TextObjs | None:
#         # text_objs = TextObjs(texts=[])
#         # vector search
#         search_results = await self.datastore._get_relevant_documents(action_input.text)
#         client = OpenAI(api_key=SettingsProvider.sget().OPENAI_API_KEY)
#
#         # if len(search_results) == 0:
#         #     return None
#         # context = "Only use relevant context to give response. If the context is insufficient say \"Cannot answer from given context\"\nContext: \n"
#         # for result in search_results:
#         #     context = f"{context}{result}\n"
#         # LM chat
#         processed_context = split_image_text_types(search_results)
#         prompt = img_prompt_func(processed_context, action_input.text)
#         response = client.chat.completions.create(model="gpt-4-vision-preview",
#             messages=prompt)
#         # message = ChatCompletionUserMessageParam(role=Role.user.value, content=f"{context}Question: {action_input.text}")
#         # self.action_config.chat_req.messages = self.action_config.chat_req.messages + [message]
#         # self.action_config.input = action_input
#         # # chat_res = await get_openai().openai_chat.chat(chat_req=self.action_config.chat_req)
#         #     action_results.texts.append(TextObj(text=choice.message.content))
#         return response
