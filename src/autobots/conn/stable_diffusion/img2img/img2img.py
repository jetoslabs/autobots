import time

import requests
from pydantic import ValidationError

from src.autobots.conn.stable_diffusion.img2img.img2img_model import SDImg2ImgReqModel, SDImg2ImgResError, \
    SDImg2ImgResModel, SDImg2ImgProcessingModel
from src.autobots.core.logging.log import Log


async def sd_img2img(req: SDImg2ImgReqModel, max_retry=3) -> SDImg2ImgResError | SDImg2ImgProcessingModel | SDImg2ImgResModel:
    url = "https://stablediffusionapi.com/api/v3/img2img"

    payload = req.model_dump_json()

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        Log.error(f"Stable diffusion Img2Img error: {response.status_code}")

    response_json = response.json()
    try:
        if response_json["status"] == "failed" and max_retry>0:
            time.sleep(3)
            return await sd_img2img(req, max_retry-1)
        elif response_json["status"] == "error":
            Log.error(f"Stable diffusion text2img error: {response_json}")
            err = SDImg2ImgResError.model_validate(response_json)
            return err
        elif response_json["status"] == "processing":
            res = SDImg2ImgProcessingModel.model_validate(response_json)
            return res
        else:
            res = SDImg2ImgResModel.model_validate(response_json)
            return res
    except ValidationError or TypeError as e:
        Log.error(f"Stable diffusion img2img validation error for response: {str(e)}")
