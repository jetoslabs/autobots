import time

import requests
from loguru import logger

from pydantic import ValidationError

from src.autobots.conn.stable_diffusion.image_mixer.image_mixer_model import (
    ImageMixerReqModel,
    ImageMixerResError,
    ImageMixerProcessingResModel,
    ImageMixerResModel,
)


async def image_mixer(
    req: ImageMixerReqModel, max_retry=3
) -> ImageMixerResModel | ImageMixerProcessingResModel | ImageMixerResError:
    """
    Reference: https://docs.modelslab.com/image-editing/imagemixer
    """
    url = "https://modelslab.com/api/v6/image_editing/img_mixer"

    payload = req.model_dump_json()

    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        logger.error(f"Stable diffusion image_mixer error: {response.status_code}")

    response_json = response.json()
    try:
        if response_json["status"] == "failed" and max_retry > 0:
            time.sleep(30)
            return await image_mixer(req, max_retry - 1)
        elif response_json["status"] == "error":
            logger.error(f"Stable diffusion text2img error: {response_json}")
            err = ImageMixerResError.model_validate(response_json)
            return err
        elif response_json["status"] == "processing":
            res = ImageMixerProcessingResModel.model_validate(response_json)
            return res
        else:
            res = ImageMixerResModel.model_validate(response_json)
            return res
    except ValidationError or TypeError:
        logger.error(
            f"Stable diffusion image_mixer validation error for response: {response_json}"
        )
