import requests

from pydantic import ValidationError

from autobots.conn.stable_diffusion.text2img.text2img_model import Text2ImgReqModel, Text2ImgResModel, \
    Text2ImgResProcessingModel, Text2ImgResError
from autobots.core.logging.log import Log


async def text2img(req: Text2ImgReqModel) -> Text2ImgResModel | Text2ImgResProcessingModel | Text2ImgResError:
    url = "https://stablediffusionapi.com/api/v3/text2img"

    payload = req.model_dump_json()

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        Log.error(f"Stable diffusion text2img error: {response.status_code}")

    response_json = response.json()
    try:
        if response_json["status"] == "error":
            Log.error(f"Stable diffusion text2img error: {response_json['message']}")
            err = Text2ImgResError.model_validate(response_json)
            return err
        elif response_json["status"] == "processing":
            res = Text2ImgResProcessingModel.model_validate(response_json)
            return res
        else:
            res = Text2ImgResModel.model_validate(response_json)
            return res
    except ValidationError or TypeError as e:
        Log.error(f"Stable diffusion text2img validation error for response: {response_json}")
