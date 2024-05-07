from serpapi import GoogleSearch
from pydantic import BaseModel, Field
from typing import Optional, List
from src.autobots.core.settings import SettingsProvider
import json


class SerpConfig(BaseModel):
    serp_apikey: Optional[str] = Field(default=SettingsProvider.sget().SERP_API_KEY,
                                        description="Serp apikey used for request authorization.")

class SerpRequest(BaseModel):
    query: str
    location: str

class Product(BaseModel):
    title: str | None
    link: str | None
    extensions: List[str] | None

class Sitelink(BaseModel):
    title: str | None
    link: str | None

class Ad(BaseModel):
    title: str | None = None
    link: str | None = None
    tracking_link: str | None = None
    displayed_link: str | None = None
    source: str | None = None
    position: int | None = None
    block_position: dict | str | None = None
    description: str | dict | None = None
    products: dict | str | None = None
    sitelinks: List[dict] | None = None

class Ads(BaseModel):
    ads: List[Ad]


async def get_local_ads(req: SerpRequest) -> Ads:
    serpApiConfig = SerpConfig()
    params = {
        "q": req.query,
        "location": req.location,
        "hl": "en",
        "gl": "us",
        "api_key": serpApiConfig.serp_apikey
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    # Check if ads key exists in results
    if "ads" in results:
        ads_data = results["ads"]
        resp =  Ads.model_validate({"ads" : ads_data})
        return resp
    else:
        return None  # Return None if ads key is not found

#
# async def get_organic_ads(req: SerpRequest) -> LocalAds:
#     serpApiConfig = SerpConfig()
#     params = {
#         "q": req.query,
#         "location": req.location,
#         "hl": "hi",
#         "gl": "in",
#         "api_key": serpApiConfig.serp_apikey
#     }
#
#     search = GoogleSearch(params)
#     results = search.get_dict()
#
#     # Check if ads key exists in results
#     if "ads" in results:
#         return LocalAds(**results["ads"])
#     else:
#         return None  # Return None if ads key is not found
#
# async def get_ads(req: SerpRequest) -> LocalAds:
#     serpApiConfig = SerpConfig()
#     params = {
#         "q": req.query,
#         "location": req.location,
#         "hl": "en",
#         "gl": "us",
#         "api_key": serpApiConfig.serp_apikey
#     }
#
#     search = GoogleSearch(params)
#     results = search.get_dict()
#
#     # Check if ads key exists in results
#     if "ads" in results:
#         return LocalAds(**results["ads"])
#     else:
#         return None  # Return None if ads key is not found

