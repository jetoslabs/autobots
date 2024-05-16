from functools import lru_cache

from httpx import Timeout
from openai import AsyncOpenAI

from src.autobots.conn.openai.openai_assistants.openai_assistants import OpenaiAssistants
from src.autobots.conn.openai.openai_audio.openai_audio import OpenaiAudio
from src.autobots.conn.openai.openai_chat.openai_chat import OpenaiChat
from src.autobots.conn.openai.openai_embeddings.openai_embeddings import OpenaiEmbeddings
from src.autobots.conn.openai.openai_files.openai_files import OpenaiFiles
from src.autobots.conn.openai.openai_images.openai_images import OpenaiImages
from src.autobots.conn.openai.openai_vector_stores.openai_vector_store_file_batches.openai_vector_store_file_batches import \
    OpenaiVectorStoreFileBatches
from src.autobots.conn.openai.openai_vector_stores.openai_vector_store_files.openai_vector_store_files import \
    OpenaiVectorStoreFiles
from src.autobots.conn.openai.openai_vector_stores.openai_vector_stores.openai_vector_stores import OpenaiVectorStores

from src.autobots.core.settings import Settings, SettingsProvider


class OpenAI:

    def __init__(self, *,
                 api_key: str | None = None,
                 organization: str | None = None,
                 timeout: float | Timeout | None = None
                 ):
        self.client = AsyncOpenAI(api_key=api_key, organization=organization, timeout=timeout)
        self.openai_audio = OpenaiAudio(self.client)
        self.openai_chat = OpenaiChat(self.client)
        self.openai_embeddings = OpenaiEmbeddings(self.client)
        self.openai_images = OpenaiImages(self.client)
        self.openai_assistants = OpenaiAssistants(self.client)
        self.openai_files = OpenaiFiles(self.client)
        self.openai_vector_stores = OpenaiVectorStores(self.client)
        self.openai_vector_store_files = OpenaiVectorStoreFiles(self.client)
        self.openai_vector_store_file_batches = OpenaiVectorStoreFileBatches(self.client)


@lru_cache
def get_openai(settings: Settings = SettingsProvider.sget()) -> OpenAI:
    return OpenAI(
        api_key=settings.OPENAI_API_KEY,
        organization=settings.OPENAI_ORG_ID,
        timeout=60.0
    )
