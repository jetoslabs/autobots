from functools import lru_cache

import supabase

from src.autobots.core.settings import Settings, SettingsProvider


class Supabase:
    def __init__(self, settings: Settings):
        self.client: supabase.Client = supabase.create_client(
            supabase_url=settings.SUPABASE_URL, supabase_key=settings.SUPABASE_ANON_KEY
        )


@lru_cache
def get_supabase(settings: Settings = SettingsProvider.sget()) -> Supabase:
    return Supabase(settings)
