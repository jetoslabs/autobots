from pathlib import Path

import replicate.client
from loguru import logger
from pydantic import BaseModel, Field, HttpUrl
from replicate.model import Model


class YanOpsFaceSwapParams(BaseModel):
    target_image: str
    source_image: str | None = None
    request_id: str | None = None
    det_thresh: float = 0.1
    local_target: Path | None = None
    local_source: Path | None = None
    cache_days: int = Field(10, ge=1, le=10)
    weight: float = Field(0.5, ge=0.1, le=1.0)


class YanOpsFaceSwapOutParams(BaseModel):
    msg: str
    code: int
    image: HttpUrl
    status: str


class YanOpsFaceSwap:
    model = "yan-ops/face_swap"

    def __init__(self, client: replicate.client.Client):
        self.client = client

    async def run(
        self, face_swap_params: YanOpsFaceSwapParams
    ) -> YanOpsFaceSwapOutParams | None:
        try:
            model: Model = self.client.models.get(YanOpsFaceSwap.model)
            ref = f"{model.id}:{model.latest_version.id}"
            output_dict = await self.client.async_run(
                ref, face_swap_params.model_dump(exclude_none=True)
            )
            output = YanOpsFaceSwapOutParams.model_validate(output_dict)
            return output
        except Exception as e:
            logger.error(str(e))
