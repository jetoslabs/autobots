import pytest
from src.autobots.conn.claid.claid import UseClaidAiApi
from src.autobots.conn.claid.claid_model import ClaidRequestModel, ClaidResponseData, Operations, Output, \
    BackgroundRemove, Background, ClaidResponse, ClaidPhotoShootRequestModel, PhotoshootOutput, PhotoshootObject, \
    PhotoshootScene, ClaidPhotoShootOutputModel, ClaidPhotoShootInputModel
from src.autobots.conn.serp.serp_ads.serp_ads import Ads, SerpRequest
from src.autobots.conn.serp.serp import UseSerpApi


@pytest.mark.asyncio
async def test_local_ads(set_test_settings):
    serp_request = SerpRequest(
        query = "coffee mug",
        location = "delhi"
    )
    usa = UseSerpApi()
    res : Ads = await usa.getLocalAds(serp_request)
    print(res)
    assert (res)




