from functools import lru_cache

from autobots.core.settings import Settings, SettingsProvider


class GoogleBard:
    def __init__(self, cookie_key: str):
        self.cookie_key = cookie_key


@lru_cache
def get_openai(settings: Settings = SettingsProvider.sget()) -> GoogleBard:
    return GoogleBard(cookie_key=settings.OPENAI_API_KEY)