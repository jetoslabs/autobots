from typing import Optional

import google.generativeai as genai
from google.generativeai.types import (
    AsyncGenerateContentResponse,
)
from loguru import logger
from retry import retry

from src.autobots.conn.google.google_genai_chat.chat_model import ChatReq, ModelName


class GoogleGenAIChat:
    def __init__(self, model_name: str = ModelName.GEMINI_PRO):
        self.model = genai.GenerativeModel(model_name)

    def set_model(self, model_name: Optional[str]):
        if model_name and self.model.model_name != model_name:
            self.model = genai.GenerativeModel(model_name)

    @retry(exceptions=Exception, tries=3, delay=30)
    async def chat(
        self,
        chat_req: ChatReq,
        model_name: Optional[str] = None,
    ) -> AsyncGenerateContentResponse:
        self.set_model(model_name)

        try:
            logger.trace("Starting GoogleGenAI Chat, try: 1")
            res: AsyncGenerateContentResponse = await self.model.generate_content_async(
                **chat_req.model_dump(exclude_none=True)
            )
            logger.trace("Completed GoogleGenAI Chat")
            return res
        except Exception as e:
            logger.error(str(e))
            raise
