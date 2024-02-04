import requests
from loguru import logger

from pydantic import ValidationError

from src.autobots.conn.stable_diffusion.text2img.text2img_model import Text2ImgReqModel, Text2ImgResModel, \
    Text2ImgResProcessingModel, Text2ImgResError


async def text2img(req: Text2ImgReqModel) -> Text2ImgResModel | Text2ImgResProcessingModel | Text2ImgResError:
    """
    Reference: https://docs.modelslab.com/realtime-stable-diffusion/text2img
    """
    url = "https://modelslab.com/api/v6/realtime/text2img"

    payload = req.model_dump_json()

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        logger.error(f"Stable diffusion text2img error: {response.status_code}")

    response_json = response.json()
    try:
        if response_json["status"] == "error":
            logger.error(f"Stable diffusion text2img error: {response_json['message']}")
            err = Text2ImgResError.model_validate(response_json)
            return err
        elif response_json["status"] == "processing":
            res = Text2ImgResProcessingModel.model_validate(response_json)
            return res
        else:
            res = Text2ImgResModel.model_validate(response_json)
            return res
    except ValidationError or TypeError as e:
        logger.error(f"Stable diffusion text2img validation error for response: {response_json}")
