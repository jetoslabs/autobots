from functools import lru_cache

import tiktoken

from src.autobots.core.settings import Settings, SettingsProvider


class Tiktoken:
    def __init__(self, model: str):
        self.enc = tiktoken.encoding_for_model(model)

    def token_count(self, text: str) -> int:
        tokens = self.enc.encode(text=text)
        return len(tokens)


@lru_cache
def get_tiktoken(settings: Settings = SettingsProvider.sget()) -> Tiktoken:
    return Tiktoken(model="gpt-4")
