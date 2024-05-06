from serpapi import GoogleSearch
from pydantic import BaseModel, Field
from typing import Optional, List
from src.autobots.core.settings import SettingsProvider


class SerpConfig(BaseModel):
    serp_apikey: Optional[str] = Field(default=SettingsProvider.sget().SERP_API_KEY,
                                        description="Serp apikey used for request authorization.")

class SerpRequest(BaseModel):
    query: str
    location: str

class LocalAd(BaseModel):
    title: str
    rating: Optional[float]
    service_area: str
    hours: str
    phone: str

class LocalAds(BaseModel):
    see_more_text: str
    badge: str
    ads: List[LocalAd]


async def get_local_ads(req: SerpRequest) -> LocalAds:
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
        return LocalAds(**results["ads"])
    else:
        return None  # Return None if ads key is not found


async def get_organic_ads(req: SerpRequest) -> LocalAds:
    serpApiConfig = SerpConfig()
    params = {
        "q": req.query,
        "location": req.location,
        "hl": "hi",
        "gl": "in",
        "api_key": serpApiConfig.serp_apikey
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    # Check if ads key exists in results
    if "ads" in results:
        return LocalAds(**results["ads"])
    else:
        return None  # Return None if ads key is not found

async def get_ads(req: SerpRequest) -> LocalAds:
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
        return LocalAds(**results["ads"])
    else:
        return None  # Return None if ads key is not found

