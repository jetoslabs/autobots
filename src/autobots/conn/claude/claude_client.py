from functools import lru_cache
from src.autobots.core.settings import Settings, SettingsProvider

from httpx import Timeout
from anthropic import AsyncAnthropic
from src.autobots.conn.claude.claude_chat import AnthropicChat
class Claude:

    def __init__(self, *,
                 api_key: str | None = None,
                 organization: str | None = None,
                 timeout: float | Timeout | None = None
                 ):
        self.client = AsyncAnthropic(api_key=api_key, timeout=timeout)
        self.claude_chat = AnthropicChat(self.client)


@lru_cache
def get_claude(settings: Settings = SettingsProvider.sget()) -> claude:
    return Claude(
        api_key=settings.CLAUDE_API_KEY,
        timeout=60.0
    )