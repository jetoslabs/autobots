import requests
import time


from pydantic import ValidationError

from src.autobots.conn.useapi.text2img.text2img_model import DiscordReqModel, DiscordJobsApiResponse, \
    DiscordErrorResponse, DiscordImagineApiResponse, DiscordButtonJobResponse
from loguru import logger
from typing import Optional
from pydantic import BaseModel, Field
from src.autobots.core.settings import SettingsProvider

class UseApiConfig(BaseModel):
    discord_server_id: Optional[str] = Field(default=SettingsProvider.sget().DISCORD_SERVER_ID,
                                             description="Your discord server id used for request authorization.")
    useapi_net_endpoint_url: Optional[str] = Field(default=SettingsProvider.sget().USEAPI_NET_END_POINT_URL,
                                                   description="USE_API end point")
    discord_token: Optional[str] = Field(default=SettingsProvider.sget().DISCORD_TOKEN,
                                         description="Your discord token used for request authorization.")
    discord_channel_id: Optional[str] = Field(default=SettingsProvider.sget().DISCORD_CHANNEL_ID,
                                              description="Your discord channel id used for request authorization.")
    use_api_net_token: Optional[str] = Field(default=SettingsProvider.sget().USEAPI_NET_TOKEN,
                                             description="Your use aoi net token id used for request authorization.")

async def imagineApi(req: DiscordReqModel) -> DiscordJobsApiResponse | DiscordErrorResponse:
    useApiConfig = UseApiConfig()
    url = useApiConfig.useapi_net_endpoint_url + 'v2/jobs/imagine'

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {useApiConfig.use_api_net_token}"
    }
    body = {
        "prompt": f"{req.prompt}",
        "discord": f"{useApiConfig.discord_token}",
        "server": f"{useApiConfig.discord_server_id}",
        "channel": f"{useApiConfig.discord_channel_id}"
    }

    response = requests.request("POST", url, headers=headers, json=body)
    if response.status_code != 200:
        logger.error(f"Mid journey text2img error: {response.status_code}")

    response_json = response.json()
    try:
        if response_json["code"] != 200:
            logger.error(f"Mid journey text2img error: {response_json['error']}")
            err = DiscordErrorResponse.model_validate(response_json)
            return err
        else:
            res = DiscordImagineApiResponse.model_validate(response_json)
            retry_count = 0
            while True:
                job_res = await jobApi(res.jobid)
                if job_res.code == 200 and job_res.status == 'completed':
                    return DiscordJobsApiResponse.model_validate(job_res)
                else:
                    retry_count += 1
                    if retry_count >= 15:  # Maximum of 5 retries
                        logger.error("Maximum retry limit reached")
                        break  # Exit the loop if maximum retry limit is reached
                    logger.warning(f"Retrying jobApi, attempt {retry_count}")
                    time.sleep(15)

            logger.error(f"Mid journey text2img error for job id: {res.jobid}")
            response_json = {"error"}
            err = DiscordErrorResponse(error="Mid Journey job fetch failed", code=500)
            return err
    except ValidationError or TypeError as e:
        logger.error(f"Mid journey text2img validation error for response: {response_json}")
        return e

async def buttonApi(req: DiscordReqModel) -> DiscordJobsApiResponse | DiscordErrorResponse:
    useApiConfig = UseApiConfig()
    url = useApiConfig.useapi_net_endpoint_url + 'v2/jobs/button'

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {useApiConfig.use_api_net_token}"
    }
    body = {
        "jobid": f"{req.job_id}",
        "button": f"{req.button}"
    }

    response = requests.request("POST", url, headers=headers, json=body)
    if response.status_code != 200:
        logger.error(f"Mid journey text2img error: {response.status_code}")

    response_json = response.json()
    try:
        if response_json["code"] != 200:
            logger.error(f"Mid journey text2img error in button api: {response_json['message']}")
            err = DiscordErrorResponse.model_validate(response_json)
            return err
        else:
            res = DiscordButtonJobResponse.model_validate(response_json)
            retry_count = 0
            while True:
                job_res = await jobApi(res.jobid)
                if job_res.code == 200 and job_res.status == 'completed':
                    return job_res
                else:
                    retry_count += 1
                    if retry_count >= 15:  # Maximum of 5 retries
                        logger.error("Maximum retry limit reached")
                        break  # Exit the loop if maximum retry limit is reached
                    logger.warning(f"Retrying jobApi, attempt {retry_count}")
                    time.sleep(15)

            logger.error(f"Mid journey text2img error for job id: {res.jobid}")
            response_json = {"error"}
            err = DiscordErrorResponse(error="Mid Journey job fetch failed", code=500).dict()
            return err

    except ValidationError or TypeError:
        logger.error(f"Mid journey text2img validation error for button api response: {response_json}")

async def jobApi(jobId) -> DiscordJobsApiResponse | DiscordErrorResponse:

    useApiConfig = UseApiConfig()
    job_id_string = jobId
    index_of_job = job_id_string.find("job")

    cleaned_job_id = job_id_string[index_of_job:]
    url = useApiConfig.useapi_net_endpoint_url + f"v2/jobs/?jobid={cleaned_job_id}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {useApiConfig.use_api_net_token}"
    }

    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        logger.error(f"Mid journey text2img error: {response.status_code}")

    response_json = response.json()
    try:
        if response_json["code"] != 200:
            logger.error(f"Mid journey text2img error: {response_json['message']}")
            err = DiscordErrorResponse.model_validate(response_json)
            return err
        else:
            res = DiscordJobsApiResponse.model_validate(response_json)
            return res
    except ValidationError or TypeError:
        logger.error(f"Mid journey text2img validation error for response: {response_json}")
