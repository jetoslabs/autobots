import requests

from pydantic import ValidationError

from src.autobots.conn.stable_diffusion.text2video.text2video_model import Text2VideoReqModel, Text2VideoResModel, \
    Text2VideoProcessingResModel, Text2VideoResError
from src.autobots.core.logging.log import Log


async def text2video(req: Text2VideoReqModel) -> Text2VideoResModel | Text2VideoProcessingResModel | Text2VideoResError:
    url = "https://stablediffusionapi.com/api/v5/text2video"

    payload = req.model_dump_json()

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        Log.error(f"Stable diffusion text2video error: {response.status_code}")

    response_json = response.json()
    try:
        if response_json["status"] == "error":
            Log.error(f"Stable diffusion text2img error: {response_json['message']}")
            err = Text2VideoResError.model_validate(response_json)
            return err
        elif response_json["status"] == "processing":
            res = Text2VideoProcessingResModel.model_validate(response_json)
            return res
        else:
            res = Text2VideoResModel.model_validate(response_json)
            return res
    except ValidationError or TypeError as e:
        Log.error(f"Stable diffusion text2img validation error for response: {response_json}")
