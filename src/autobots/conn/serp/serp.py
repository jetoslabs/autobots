from functools import lru_cache
from src.autobots.conn.serp.serp_ads.serp_ads import get_local_ads, SerpRequest, Ads


class UseSerpApi:

    async def getLocalAds(self, req: SerpRequest) -> Ads:
        resp : Ads = await get_local_ads(req)
        return resp

@lru_cache
def get_serp_ai() -> UseSerpApi:
    return UseSerpApi()