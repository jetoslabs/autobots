from functools import lru_cache

from openai import AsyncOpenAI

from autobots.conn.openai.openai_audio.openai_audio import OpenaiAudio
from autobots.conn.openai.openai_chat.openai_chat import OpenaiChat
from autobots.conn.openai.openai_embeddings.openai_embeddings import OpenaiEmbeddings
from autobots.conn.openai.openai_images.openai_images import OpenaiImages

from autobots.core.settings import Settings, SettingsProvider


class OpenAI:

    def __init__(self, org_id: str, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key,organization=org_id,timeout=180)
        self.openai_audio = OpenaiAudio(self.client)
        self.openai_chat = OpenaiChat(self.client)
        self.openai_embeddings = OpenaiEmbeddings(self.client)
        self.openai_images = OpenaiImages(self.client)



@lru_cache
def get_openai(settings: Settings = SettingsProvider.sget()) -> OpenAI:
    return OpenAI(settings.OPENAI_ORG_ID, settings.OPENAI_API_KEY)
