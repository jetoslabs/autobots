from functools import lru_cache

from autobots.conn.openai.openai import OpenAI
from autobots.core.settings import Settings, get_settings


class Resource:

    def __init__(self, settings: Settings):
        # setting up OpenAI
        OpenAI(settings.OPENAI_ORG_ID, settings.OPENAI_API_KEY)


@lru_cache
def get_resource(settings: Settings = get_settings()) -> Resource:
    return Resource(settings)

