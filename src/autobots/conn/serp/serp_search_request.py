from typing import Optional, Literal

from pydantic import BaseModel


class SearchQuery(BaseModel):
    q: str


class GeographicLocation(BaseModel):
    location: Optional[str] = None


class Localization(BaseModel):
    google_domain: Optional[str] = None
    gl: Optional[str] = None
    hl: Optional[str] = None
    cr: Optional[str] = None
    lr: Optional[str] = None


class AdvancedFilters(BaseModel):
    tbs: Optional[str] = None
    safe: Optional[Literal["active", "off"]] = None
    nfpr: Optional[Literal["0", "1"]] = None
    filter: Optional[Literal["0", "1"]] = None


class SearchType(BaseModel):
    tbm: Optional[Literal["isch", "lcl", "vid", "nws", "shop", "pts"]] = None


class Pagination(BaseModel):
    start: Optional[int] = None
    num: Optional[int] = None


class SerpapiParameters(BaseModel):
    engine: Literal["google"] = "google"
    device: Optional[Literal["desktop", "tablet", "mobile"]] = None
    no_cache: Optional[bool] = None
    # api_key: str
    output: Optional[Literal["JSON", "html"]] = None


class SerpGoogleSearchParams(
    SearchQuery,
    GeographicLocation,
    Localization,
    AdvancedFilters,
    SearchType,
    Pagination,
    SerpapiParameters
):
    pass
