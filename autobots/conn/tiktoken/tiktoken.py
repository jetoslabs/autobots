from functools import lru_cache

import tiktoken

from autobots.core.settings import Settings, get_settings


class Tiktoken:

    def __init__(self, model: str = "gpt-4"):
        self.enc = tiktoken.encoding_for_model(model)

    def token_count(self, text: str) -> int:
        tokens = self.enc.encode(text=text)
        return len(tokens)


@lru_cache
def get_tiktoken(settings: Settings = get_settings()) -> Tiktoken:
    return Tiktoken()
