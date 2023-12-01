from openai import AsyncOpenAI
from openai.types import ImagesResponse

from autobots.conn.openai.openai_images.image_model import ImageReq
from autobots.core.logging.log import Log


class OpenaiImages():

    def __init__(self, openai_client: AsyncOpenAI):
        self.client = openai_client

    async def create_image(self, image_req: ImageReq) -> ImagesResponse | None:
        try:
            Log.trace("Starting OpenAI create image")
            res: ImagesResponse = await self.client.images.generate(**image_req.model_dump())
            Log.trace("Completed OpenAI create image")
            return res
        except Exception as e:
            Log.error(str(e))
