from functools import lru_cache
import requests
from autobots.conn.useapi.common_models import DiscordImagineApiResponse, DiscordJobsApiResponse
from autobots.core.settings import Settings, SettingsProvider

class UseApi:
    def __init__(self, discord_server_id: str, discord_token: str, discord_channel_id: str, useapi_net_token: str, useapi_net_endpoint_url: str):
        self.discord_server_id = discord_server_id
        self.discord_token = discord_token
        self.discord_channel_id = discord_channel_id
        self.useapi_net_token = useapi_net_token
        self.useapi_net_endpoint_url = useapi_net_endpoint_url


    async def imagine(self, prompt: str) -> DiscordImagineApiResponse:
        apiUrl = self.useapi_net_endpoint_url+'v2/jobs/imagine'
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.useapi_net_token}"
        }
        body = {
            "prompt": f"{prompt}",
            "discord": f"{self.discord_token}",
            "server": f"{self.discord_server_id}",
            "channel": f"{self.discord_channel_id}"
        }
        return requests.post(apiUrl, headers=headers, json=body)

    async def jobs(self, jobid: str) -> DiscordJobsApiResponse:
        apiUrl = self.useapi_net_endpoint_url+f"v2/jobs/?jobid={jobid}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.useapi_net_token}"
        }
        return requests.post(apiUrl, headers=headers)


@lru_cache
def get_unstructured_io(settings: Settings = SettingsProvider.sget()) -> UseApi:
    return UseApi(settings.DISCORD_SERVER_ID, settings.DISCORD_TOKEN, settings.DISCORD_CHANNEL_ID,  settings.USEAPI_NET_TOKEN, settings.USEAPI_NET_END_POINT_URL)
