import time
from typing import List

import requests
import json

from pydantic import BaseModel

from autobots.conn.stable_diffusion.common_models import StableDiffusionResStatus
from autobots.core.settings import SettingsProvider


class FetchQueuedImagesProcessingResModel(BaseModel):
    status: StableDiffusionResStatus
    messege: str
    output: str


class FetchQueuedImagesResModel(BaseModel):
    status: StableDiffusionResStatus
    id: int
    output: List[str]


async def fetch_queued_image(
        id: str, key: str = SettingsProvider.sget().STABLE_DIFFUSION_API_KEY, max_retry=3
) -> FetchQueuedImagesResModel | FetchQueuedImagesProcessingResModel:

    url = f"https://stablediffusionapi.com/api/v3/fetch/{id}"

    payload = json.dumps({
        "key": key
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    response_json = response.json()
    if response_json["status"] == "failed" and max_retry > 0:
        time.sleep(7 - max_retry)
        return await fetch_queued_image(id, key, max_retry - 1)
    elif response_json["status"] == StableDiffusionResStatus.processing.value and max_retry > 0:
        time.sleep(7 - max_retry)
        return await fetch_queued_image(id, key, max_retry - 1)
        # res = FetchQueuedImagesProcessingResModel.model_validate(response_json)
        # return res
    elif response_json["status"] == StableDiffusionResStatus.success.value:
        res = FetchQueuedImagesResModel.model_validate(response_json)
        return res
