from functools import lru_cache

import google.generativeai

from src.autobots.conn.google.google_genai_chat.google_genai_chat import GoogleGenAIChat
from src.autobots.core.settings import Settings, SettingsProvider


class GoogleGenAI:
    def __init__(
        self,
        *,
        api_key: str | None = None,
    ):
        google.generativeai.configure(api_key=api_key)
        self.google_genai_chat = GoogleGenAIChat()


@lru_cache
def get_google_genai(settings: Settings = SettingsProvider.sget()) -> GoogleGenAI:
    return GoogleGenAI(
        api_key=settings.GOOGLE_AI_API_KEY,
    )
