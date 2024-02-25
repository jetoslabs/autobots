from functools import lru_cache
from src.autobots.conn.useapi.text2img.text2img_model import DiscordReqModel, DiscordJobsApiResponse, \
    DiscordErrorResponse, DiscordImagineApiResponse
from src.autobots.conn.useapi.text2img.text2img import imagineApi, jobApi


class UseApi:

    async def imagine(self, req: DiscordReqModel) -> DiscordImagineApiResponse | DiscordErrorResponse:

        res: DiscordImagineApiResponse | DiscordErrorResponse = await imagineApi(req)
        return res

    async def jobs(self, req: DiscordReqModel) -> DiscordJobsApiResponse | DiscordErrorResponse:

        res: DiscordJobsApiResponse | DiscordErrorResponse = await jobApi(req)
        return res


@lru_cache
def get_use_api_net() -> UseApi:
    return UseApi()
