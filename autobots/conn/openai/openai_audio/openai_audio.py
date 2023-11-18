import os

import httpx
from httpx import URL
from openai import AsyncOpenAI
from openai._base_client import HttpxBinaryResponseContent
from openai.types.audio import Transcription, Translation
from pydantic import HttpUrl

from autobots.conn.openai.openai_audio.speech_model import SpeechReq
from autobots.conn.openai.openai_audio.transcription_model import TranscriptionReq
from autobots.conn.openai.openai_audio.translation_model import TranslationReq
from autobots.core.log import log


class OpenaiAudio():

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

    async def speech(self, speech_req: SpeechReq) -> HttpxBinaryResponseContent | None:
        try:
            log.trace("Starting OpenAI create speech")
            res = await self.client.audio.speech.create(**speech_req.model_dump())
            log.trace("Completed OpenAI create speech")
            return res
        except Exception as e:
            log.exception(str(e))

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
                res = await self.client.audio.transcriptions.create(file=binary_file,
                                                                    **transcription_req.model_dump(exclude_none=True))
                log.trace("Completed OpenAI create transcription")
            return res
        except Exception as e:
            log.exception(str(e))
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
                res = await self.client.audio.translations.create(file=binary_file,
                                                                  **translation_req.model_dump(exclude_none=True))
                log.trace("Completed OpenAI create translation")
            return res
        except Exception as e:
            log.exception(str(e))
        finally:
            # delete the file
            os.remove(full_path_name)
