from functools import lru_cache

from bardapi import Bard
from bardapi.models.result import BardResult

from autobots.conn.google.bard.google_bard_model import GoogleBardAsk
from autobots.core.settings import Settings, SettingsProvider


class GoogleBard:
    def __init__(self, cookie_key: str):
        self.client = Bard(token=cookie_key,
                           timeout=180,
                           proxies=None,
                           session=None,
                           conversation_id=None,
                           google_translator_api_key=None,
                           language=None,
                           run_code=True,
                           token_from_browser=False)

    async def ask(self, ask_params: GoogleBardAsk) -> BardResult:
        result: BardResult = self.client.ask(**ask_params.model_dump(exclude_none=True))
        return result


@lru_cache
def get_google_bard(settings: Settings = SettingsProvider.sget()) -> GoogleBard:
    return GoogleBard(cookie_key=settings.OPENAI_API_KEY)
