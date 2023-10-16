import time
from typing import List, Optional, Any, Dict

import requests

from pydantic import BaseModel, Field, ValidationError, HttpUrl

from autobots.conn.stable_diffusion.common_models import StableDiffusionResStatus
from autobots.core.log import log
from autobots.core.settings import SettingsProvider


class ImageMixerReqModel(BaseModel):
    key: str = Field(default=SettingsProvider.sget().STABLE_DIFFUSION_API_KEY,
                     description="Your API Key used for request authorization")
    prompt: str = Field(...,
                        description="Text prompt with description of the things you want in the image to be generated")
    negative_prompt: Optional[str] = Field(default=None, description="Items you don't want in the image")
    init_image: str = Field(..., description="comma separated image urls of images to mix")
    width: int = Field(default=512, ge=1, le=1024, description="Width of the image. Max Height: Width: 1024x1024")
    height: int = Field(default=512, ge=1, le=1024, description="Height of the image. Max Height: Width: 1024x1024")
    steps: int = Field(default=30, ge=1, le=50, description="Number of denoising steps (minimum: 1; maximum: 50)")
    guidance_scale: float = Field(default=10, ge=1, le=20,
                                  description="Scale for classifier-free guidance (minimum: 1; maximum: 20)")
    init_image_weights: str = Field(...,
                                            description="weight of the images being passed separated by comma. Min 0 and Max 1")
    seed: Optional[int] = Field(None,
                                description="Seed is used to reproduce results, same seed will give you same image in return again. Pass null for a random number.")
    samples: int = Field(default=1, ge=1, le=4,
                         description="Number of images to be returned in response. The maximum value is 4.")
    webhook: Optional[str] = Field(default=None,
                                   description="Set an URL to get a POST API call once the image generation is complete.")
    track_id: Optional[str] = Field(default=None,
                                    description="This ID is returned in the response to the webhook API call. This will be used to identify the webhook request.")


class ImageMixerResMetaData(BaseModel):
    H: int
    W: int
    file_prefix: str
    guidance_scale: int
    init_image: str  # This could be List[str] if you split on commas
    init_image_weights: str  # This could be List[float] if you split on commas
    instant_response: Optional[str] = None
    n_samples: int
    negative_prompt: str
    outdir: str
    prompt: str
    seed: int
    steps: int


class ImageMixerResError(BaseModel):
    status: StableDiffusionResStatus
    messege: Optional[Dict[str, Any]] = None


class ImageMixerProcessingResModel(BaseModel):
    status: StableDiffusionResStatus
    tip: str
    eta: float
    message: Optional[str] = None
    messege: Optional[str] = None
    fetch_result: HttpUrl
    id: int
    output: List[HttpUrl]
    meta: ImageMixerResMetaData


class ImageMixerResModel(BaseModel):
    status: StableDiffusionResStatus
    generationTime: float
    id: int
    output: List[str]
    meta: ImageMixerResMetaData


async def image_mixer(
        req: ImageMixerReqModel, max_retry=3) -> ImageMixerResModel | ImageMixerProcessingResModel | ImageMixerResError:
    url = "https://stablediffusionapi.com/api/v3/img_mixer"

    payload = req.model_dump_json()

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        log.error(f"Stable diffusion image_mixer error: {response.status_code}")

    response_json = response.json()
    try:
        if response_json["status"] == "failed" and max_retry>0:
            time.sleep(3)
            return await image_mixer(req, max_retry-1)
        elif response_json["status"] == "error":
            log.error(f"Stable diffusion text2img error: {response_json}")
            err = ImageMixerResError.model_validate(response_json)
            return err
        elif response_json["status"] == "processing":
            res = ImageMixerProcessingResModel.model_validate(response_json)
            return res
        else:
            res = ImageMixerResModel.model_validate(response_json)
            return res
    except ValidationError or TypeError as e:
        log.error(f"Stable diffusion image_mixer validation error for response: {response_json}")
