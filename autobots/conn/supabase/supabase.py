from functools import lru_cache

import supabase

from autobots.core.settings import get_settings, Settings


class Supabase:

    def __init__(self, settings: Settings = get_settings()):
        self.client: supabase.Client = supabase.create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_ANON_KEY
        )


@lru_cache
def get_supabase(settings: Settings = get_settings()) -> Supabase:
    return Supabase(settings)
