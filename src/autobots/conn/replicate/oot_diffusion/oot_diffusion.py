from pathlib import Path

import replicate.client
from loguru import logger
from pydantic import BaseModel, Field, HttpUrl, validator
from replicate.model import Model
from typing import List


class OotdDiffusionInParams(BaseModel):
    model_image: str = Field(None,
                                  description="imange url")
    garment_image: str = Field(default=None, description="garmemt image")
    steps: int = Field(20, ge=1, le=40)
    guidance_scale: int = Field(2, ge=1, le=5)
    seed: int = Field(0, ge=0, le=18446744073709552000)


class OotdDiffusionOutputData(BaseModel):
    urls: List[str]



class OotdDiffusion:
    model = "viktorfa/oot_diffusion"

    def __init__(self, client: replicate.client.Client):
        self.client = client

    async def run(self, ootd_diffusion_params: OotdDiffusionInParams) -> OotdDiffusionOutputData | None:
        try:
            model: Model = self.client.models.get(OotdDiffusion.model)
            ref = f"{model.id}:{model.latest_version.id}"
            output_list = await self.client.async_run(ref, ootd_diffusion_params.model_dump(exclude_none=True))
            output = OotdDiffusionOutputData(urls=output_list)
            return output
        except Exception as e:
            logger.error(str(e))
