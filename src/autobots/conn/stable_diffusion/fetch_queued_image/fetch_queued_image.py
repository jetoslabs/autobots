import time
from typing import List

import requests
import json

from fastapi import HTTPException
from pydantic import BaseModel

from src.autobots.conn.stable_diffusion.common_models import StableDiffusionResStatus
from src.autobots.core.settings import SettingsProvider


class FetchQueuedImagesProcessingResModel(BaseModel):
    status: StableDiffusionResStatus
    messege: str
    output: str


class FetchQueuedImagesResModel(BaseModel):
    status: StableDiffusionResStatus
    id: int
    output: List[str]


async def fetch_queued_image(
        id: int,
        key: str = SettingsProvider.sget().STABLE_DIFFUSION_API_KEY,
        max_retry: int = 10,
        sleep_time: float = 30.0
) -> FetchQueuedImagesResModel | None:
    # url = f"https://stablediffusionapi.com/api/v3/fetch/{id}"
    url = f"https://modelslab.com/api/v6/realtime/fetch/{id}"

    payload = json.dumps({
        "key": key
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    response_json = response.json()
    if (response_json["status"] == "failed" or response_json["status"] == "error") and max_retry > 0:
        raise HTTPException(503, response_json)
    elif response_json["status"] == StableDiffusionResStatus.processing.value and max_retry > 0:
        time.sleep(sleep_time)
        return await fetch_queued_image(id, key, max_retry - 1, sleep_time)
    elif response_json["status"] == StableDiffusionResStatus.success.value:
        res = FetchQueuedImagesResModel.model_validate(response_json)
        return res
