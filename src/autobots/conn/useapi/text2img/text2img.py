import requests

from pydantic import ValidationError

from src.autobots.conn.useapi.text2img.text2img_model import DiscordReqModel, DiscordJobsApiResponse, \
    DiscordErrorResponse, DiscordImagineApiResponse, DiscordJobReqModel
from loguru import logger


async def imagineApi(req: DiscordReqModel) -> DiscordImagineApiResponse | DiscordErrorResponse:
    url = req.url + 'v2/jobs/imagine'

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {req.use_api_net_token}"
    }
    body = {
        "prompt": f"{req.prompt}",
        "discord": f"{req.discord_token}",
        "server": f"{req.discord_server_id}",
        "channel": f"{req.discord_channel_id}"
    }

    response = requests.request("POST", url, headers=headers, json=body)
    if response.status_code != 200:
        logger.error(f"Mid journey text2img error: {response.status_code}")

    response_json = response.json()
    try:
        if response_json["status"] == "error":
            logger.error(f"Mid journey text2img error: {response_json['message']}")
            err = DiscordErrorResponse.model_validate(response_json)
            return err
        else:
            res = DiscordImagineApiResponse.model_validate(response_json)
            return res
    except ValidationError or TypeError as e:
        logger.error(f"Mid journey text2img validation error for response: {response_json}")


async def jobApi(req: DiscordJobReqModel) -> DiscordJobsApiResponse | DiscordErrorResponse:
    url = req.url + f"v2/jobs/?jobid={req.job_id}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {req.use_api_net_token}"
    }

    response = requests.request("POST", url, headers=headers)
    if response.status_code != 200:
        logger.error(f"Mid journey text2img error: {response.status_code}")

    response_json = response.json()
    try:
        if response_json["status"] == "error":
            logger.error(f"Mid journey text2img error: {response_json['message']}")
            err = DiscordErrorResponse.model_validate(response_json)
            return err
        else:
            res = DiscordJobsApiResponse.model_validate(response_json)
            return res
    except ValidationError or TypeError as e:
        logger.error(f"Mid journey text2img validation error for response: {response_json}")
