import os
import time
from functools import lru_cache

import httpx
from httpx import URL
from openai import AsyncOpenAI, AsyncStream
from openai._base_client import HttpxBinaryResponseContent
from openai.types import CreateEmbeddingResponse, ImagesResponse
from openai.types.audio import Transcription, Translation
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from pydantic import HttpUrl

from autobots.conn.openai.chat import ChatReq
from autobots.conn.openai.embedding import EmbeddingReq, EmbeddingRes
from autobots.conn.openai.image_model import ImageReq
from autobots.conn.openai.speech_model import SpeechReq
from autobots.conn.openai.transcription_model import TranscriptionReq
from autobots.conn.openai.translation_model import TranslationReq
from autobots.core.log import log
from autobots.core.settings import Settings, SettingsProvider


class OpenAI:

    def __init__(self, org_id: str, api_key: str):
        self.client = AsyncOpenAI(
            api_key=api_key,
            organization=org_id,
            timeout=180
        )

    async def chat(self, chat_req: ChatReq) -> ChatCompletion | AsyncStream[ChatCompletionChunk] | None:
        max_retry = 3
        for i in range(max_retry):
            try:
                log.trace("Starting OpenAI Chat, try: 1")
                res: ChatCompletion = await self.client.chat.completions.create(**chat_req.model_dump(), timeout=180)
                log.trace("Completed OpenAI Chat")
                if isinstance(res, AsyncStream):
                    return self.yield_chat_chunks(res)
                else:
                    return res
            except Exception as e:
                log.exception(e)
                time.sleep(5)

    async def yield_chat_chunks(self, chat_res: AsyncStream[ChatCompletionChunk]) -> ChatCompletionChunk | None:
        try:
            async for part in chat_res:
                yield part
        except Exception as e:
            log.exception(e)

    async def embedding(self, embedding_req: EmbeddingReq) -> EmbeddingRes | None:
        try:
            log.trace("Starting OpenAI Embedding")
            res: CreateEmbeddingResponse = await self.client.embeddings.create(**embedding_req.model_dump())
            log.trace("Completed OpenAI Embedding")
            resp: EmbeddingRes = EmbeddingRes(**res.model_dump())
            return resp
        except Exception as e:
            log.exception(e)

    async def create_image(self, image_req: ImageReq) -> ImagesResponse | None:
        try:
            log.trace("Starting OpenAI create image")
            res: ImagesResponse = await self.client.images.generate(**image_req.model_dump())
            log.trace("Completed OpenAI create image")
            return res
        except Exception as e:
            log.exception(e)

    async def speech(self, speech_req: SpeechReq) -> HttpxBinaryResponseContent | None:
        try:
            log.trace("Starting OpenAI create speech")
            res = await self.client.audio.speech.create(**speech_req.model_dump())
            log.trace("Completed OpenAI create speech")
            return res
        except Exception as e:
            log.exception(e)

    async def transcription(self, transcription_req: TranscriptionReq) -> Transcription | None:
        # create new single directory
        path = "./to_del"
        if not os.path.exists(path):
            os.mkdir(path)
        # build filename
        url = HttpUrl(transcription_req.file_url)
        filename = url.path.replace("/", "")
        full_path_name = f"{path}/{filename}"
        # get data from url and create a file object
        audio_resp = httpx.Client().get(url=URL(str(transcription_req.file_url)))
        content = audio_resp.content
        with open(full_path_name, "wb") as binary_file:
            # Write bytes to file
            binary_file.write(content)
        try:
            # read file object and send to openai
            with open(full_path_name, "rb") as binary_file:
                log.trace("Starting OpenAI create transcription")
                transcription_req.file_url = None
                res = await self.client.audio.transcriptions.create(file=binary_file, **transcription_req.model_dump(exclude_none=True))
                log.trace("Completed OpenAI create transcription")
            return res
        except Exception as e:
            log.exception(e)
        finally:
            # delete the file
            os.remove(full_path_name)

    async def translation(self, translation_req: TranslationReq) -> Translation | None:
        # create new single directory
        path = "./to_del"
        if not os.path.exists(path):
            os.mkdir(path)
        # build filename
        url = HttpUrl(translation_req.file_url)
        filename = url.path.replace("/", "")
        full_path_name = f"{path}/{filename}"
        # get data from url and create a file object
        audio_resp = httpx.Client().get(url=URL(str(translation_req.file_url)))
        content = audio_resp.content
        with open(full_path_name, "wb") as binary_file:
            # Write bytes to file
            binary_file.write(content)
        try:
            # read file object and send to openai
            with open(full_path_name, "rb") as binary_file:
                log.trace("Starting OpenAI create translation")
                translation_req.file_url = None
                res = await self.client.audio.translations.create(file=binary_file, **translation_req.model_dump(exclude_none=True))
                log.trace("Completed OpenAI create translation")
            return res
        except Exception as e:
            log.exception(e)
        finally:
            # delete the file
            os.remove(full_path_name)


@lru_cache
def get_openai(settings: Settings = SettingsProvider.sget()) -> OpenAI:
    return OpenAI(settings.OPENAI_ORG_ID, settings.OPENAI_API_KEY)
