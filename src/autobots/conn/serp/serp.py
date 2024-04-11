from functools import lru_cache
from src.autobots.conn.serp.local_ads.local_ads import get_local_ads, SerpRequest, LocalAds


class UseSerpApi:

    async def getLocalAds(self, req: SerpRequest) -> LocalAds:
        resp : LocalAds = await get_local_ads(req)
        return resp

@lru_cache
def get_serp_ai() -> UseSerpApi:
    return UseSerpApi()