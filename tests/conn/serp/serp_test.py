import pytest
from src.autobots.conn.claid.claid import UseClaidAiApi
from src.autobots.conn.claid.claid_model import ClaidRequestModel, ClaidResponseData, Operations, Output, \
    BackgroundRemove, Background, ClaidResponse, ClaidPhotoShootRequestModel, PhotoshootOutput, PhotoshootObject, \
    PhotoshootScene, ClaidPhotoShootOutputModel, ClaidPhotoShootInputModel
from src.autobots.conn.serp.local_ads.local_ads import LocalAds, SerpRequest
from src.autobots.conn.serp.serp import UseSerpApi


@pytest.mark.asyncio
async def test_local_ads(set_test_settings):
    serp_request = SerpRequest(
        query = "black coffee",
        location = "abu dhabi"
    )
    usa = UseSerpApi()
    res : LocalAds = await usa.getLocalAds(serp_request)
    print(res)
    assert (res)




