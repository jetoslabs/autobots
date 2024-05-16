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

class SerpShoppingRequest(BaseModel):
    query: str

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

class InlineSitelinks(BaseModel):
    title: str | None = None
    link: str | None = None

class Sitelinks(BaseModel):
    inline: List[InlineSitelinks] | None = None

class OrganicResult(BaseModel):
    position: int | None = None
    title: str | None = None
    link: str | None = None
    redirect_link: str | None = None
    displayed_link: str | None = None
    thumbnail: str | None = None
    favicon: str | None = None
    snippet: str | None = None
    snippet_highlighted_words: List[str] | None = None
    sitelinks: Optional[Sitelinks] | None = None
    source: str | None = None
    date: Optional[str] | None = None

class OrganicResults(BaseModel):
    organic_results: List[OrganicResult]

class Extensions(BaseModel):
    extension: dict | str | None = None

class FeaturedShoppingResult(BaseModel):
    position: int | None = None
    title: str | None = None
    link: str | None = None
    product_link: str | None = None
    product_id: str | None = None
    serpapi_product_api: str | None = None
    source: str | None = None
    price: str | None = None
    extracted_price: float | None = None
    old_price: Optional[str] | None = None
    extracted_old_price: Optional[float] | None = None
    second_hand_condition: Optional[str] | None = None
    rating: float | None = None
    reviews: int | None = None
    extensions: List[str] | None
    thumbnail: str | None = None
    tag: str | None = None
    delivery: str | None = None
    store_rating: Optional[float] | None = None
    store_reviews: Optional[int] | None = None
    remark: Optional[str] | None = None
    number_of_comparisons: Optional[str] | None = None
    comparison_link: Optional[str] | None = None
    serpapi_product_api_comparisons: Optional[str] | None = None

class FeaturedShoppingResults(BaseModel):
    featured_shopping_results: List[FeaturedShoppingResult]


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

async def get_organic_results(req: SerpRequest) -> OrganicResults:
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
    if "organic_results" in results:
        organic_results = results["organic_results"]
        resp = OrganicResults.model_validate({"organic_results" : organic_results})
        return resp
    else:
        return None  # Return None if ads key is not found

async def get_shopping_results(req: SerpShoppingRequest) :
    serpApiConfig = SerpConfig()
    params = {
        "q": req.query,
        "api_key": serpApiConfig.serp_apikey,
        "engine": "google_shopping"
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    # Check if ads key exists in results
    if "featured_shopping_results" in results:
        featured_shopping_results = results["featured_shopping_results"]
        return FeaturedShoppingResults.model_validate({"featured_shopping_results" : featured_shopping_results})
    else:
        return None  # Return None if ads key is not found

