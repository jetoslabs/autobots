import time

import requests
from loguru import logger
from pydantic import ValidationError

from src.autobots.conn.stable_diffusion.img2img.img2img_model import SDImg2ImgReqModel, SDImg2ImgResError, \
    SDImg2ImgResModel, SDImg2ImgProcessingModel


async def sd_img2img(req: SDImg2ImgReqModel, max_retry=3) -> SDImg2ImgResError | SDImg2ImgProcessingModel | SDImg2ImgResModel:
    """
    Reference: https://modelslab.com/api/v6/realtime/img2img
    """
    url = "https://modelslab.com/api/v6/realtime/img2img"

    payload = req.model_dump_json()

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        logger.error(f"Stable diffusion Img2Img error: {response.status_code}")

    response_json = response.json()
    try:
        if response_json["status"] == "failed" and max_retry>0:
            time.sleep(10)
            return await sd_img2img(req, max_retry-1)
        elif response_json["status"] == "error":
            logger.error(f"Stable diffusion text2img error: {response_json}")
            err = SDImg2ImgResError.model_validate(response_json)
            return err
        elif response_json["status"] == "processing":
            res = SDImg2ImgProcessingModel.model_validate(response_json)
            return res
        else:
            res = SDImg2ImgResModel.model_validate(response_json)
            return res
    except ValidationError or TypeError as e:
        logger.error(f"Stable diffusion img2img validation error for response: {str(e)}")
