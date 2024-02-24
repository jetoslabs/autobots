from functools import lru_cache
import requests
from src.autobots.conn.useapi.text2img.text2img_model import DiscordReqModel, DiscordJobsApiResponse, \
    DiscordErrorResponse, DiscordImagineApiResponse, DiscordJobReqModel
from src.autobots.conn.useapi.text2img.text2img import imagineApi, jobApi
from src.autobots.core.settings import Settings, SettingsProvider

class UseApi:
    def __init__(self, discord_server_id: str, discord_token: str, discord_channel_id: str, useapi_net_token: str, useapi_net_endpoint_url: str):
        self.discord_server_id = discord_server_id
        self.discord_token = discord_token
        self.discord_channel_id = discord_channel_id
        self.useapi_net_token = useapi_net_token
        self.useapi_net_endpoint_url = useapi_net_endpoint_url


    async def imagine(self, req: DiscordReqModel) -> DiscordImagineApiResponse:

        req.use_api_net_token = self.useapi_net_token
        req.discord_server_id = self.discord_server_id
        req.discord_token = self.discord_token
        req.discord_channel_id = self.discord_channel_id
        req.useapi_net_endpoint_url = self.useapi_net_endpoint_url


        res: DiscordImagineApiResponse | DiscordErrorResponse = await imagineApi(req)
        return res;

    async def jobs(self, req: DiscordJobReqModel) -> DiscordJobsApiResponse:
        req.use_api_net_token = self.useapi_net_token
        req.discord_server_id = self.discord_server_id
        req.discord_token = self.discord_token
        req.discord_channel_id = self.discord_channel_id
        req.useapi_net_endpoint_url = self.useapi_net_endpoint_url

        apiUrl = self.useapi_net_endpoint_url+f"v2/jobs/?jobid={req.job_id}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.useapi_net_token}"
        }
        return requests.post(apiUrl, headers=headers)


@lru_cache
def get_use_api_net(settings: Settings = SettingsProvider.sget()) -> UseApi:
    return UseApi(settings.DISCORD_SERVER_ID, settings.DISCORD_TOKEN, settings.DISCORD_CHANNEL_ID,  settings.USEAPI_NET_TOKEN, settings.USEAPI_NET_END_POINT_URL)
