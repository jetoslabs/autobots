from pathlib import Path

import httpx
from openai import AsyncOpenAI
from openai.types import ImagesResponse
from pydantic_core import Url

from autobots.conn.openai.openai_images.image_model import ImageReq, ImageEdit, ImageCreateVariation
from autobots.core.logging.log import Log


class OpenaiImages():

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

    async def create_image(self, image_req: ImageReq) -> ImagesResponse | None:
        try:
            Log.trace("Starting OpenAI create image")
            res: ImagesResponse = await self.client.images.generate(**image_req.model_dump(exclude_none=True))
            Log.trace("Completed OpenAI create image")
            return res
        except Exception as e:
            Log.error(str(e))

    async def create_image_edit(self, image_edit_input: ImageEdit) -> ImagesResponse | None:
        try:
            # Converting image to path or bytes
            if isinstance(image_edit_input.image, Path):
                pass
            elif isinstance(image_edit_input.image, Url):
                resp = httpx.get(image_edit_input.image.unicode_string())
                image_edit_input.image = resp.content

            Log.trace("Starting OpenAI create image edit")
            res: ImagesResponse = await self.client.images.edit(**image_edit_input.model_dump(exclude_none=True))
            Log.trace("Completed OpenAI create image edit")
            return res
        except Exception as e:
            Log.error(str(e))

    async def create_image_variation(self, image_create_variation_input: ImageCreateVariation) -> ImagesResponse | None:
        try:
            # Converting image to path or bytes
            if isinstance(image_create_variation_input.image, Path):
                pass
            elif isinstance(image_create_variation_input.image, Url):
                resp = httpx.get(image_create_variation_input.image.unicode_string())
                image_create_variation_input.image = resp.content

            Log.trace("Starting OpenAI create image variation")
            res: ImagesResponse = await self.client.images.create_variation(**image_create_variation_input.model_dump(exclude_none=True))
            Log.trace("Completed OpenAI create image variation")
            return res
        except Exception as e:
            Log.error(str(e))
