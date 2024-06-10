from functools import lru_cache

from autobots.conn.serp.serp_google_search import SerpGoogleSearch
from src.autobots.core.settings import Settings, SettingsProvider


class Serp:

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.serp_google_search = SerpGoogleSearch(api_key)


@lru_cache
def get_serp(settings: Settings = SettingsProvider.sget()) -> Serp:
    return Serp(
        api_key=settings.SERP_API_KEY
    )
