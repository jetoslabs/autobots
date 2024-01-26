import requests

from pydantic import ValidationError
from retry import retry

from src.autobots.conn.stable_diffusion.text2video.text2video_model import Text2VideoReqModel, Text2VideoResModel, \
    Text2VideoProcessingResModel, Text2VideoResError
from src.autobots.core.logging.log import Log


@retry(exceptions=Exception, tries=3, delay=40)
async def text2video(req: Text2VideoReqModel) -> Text2VideoResModel | Text2VideoProcessingResModel | Text2VideoResError:
    """
    Reference: https://docs.modelslab.com/text-to-video/texttovideo
    url = "https://modelslab.com/api/v6/video/text2video"
    """
    url = "https://stablediffusionapi.com/api/v5/text2video"

    payload = req.model_dump_json(exclude_none=True)

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        Log.error(f"Stable diffusion text2video error: {response.status_code}")

    response_json = response.json()
    try:
        if response_json["status"] == "failed" or response_json["status"] == "error":
            Log.error(f"Stable diffusion text2img error: {response_json['message']}")
            if str(response_json['message']).lower().__contains__("try again"):
                raise Exception()
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
