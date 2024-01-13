from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from autobots.conn.duckduckgo.duckduckgo_region_model import Region


class Safesearch(str, Enum):
    on = "on"
    moderate = "moderate"
    off = "off"


class Timelimit(str, Enum):
    day = "d"
    week = "w"
    month = "m"
    year = "y"


class SearchTextParams(BaseModel):
    keywords: str = ""
    region: Region = Region.No_Region.value
    safesearch: Safesearch = Safesearch.moderate.value
    timelimit: Timelimit | None = None
    max_results: int = Field(3, ge=1, le=10)


class SearchMapsParams(BaseModel):
    keywords: str
    place: str
    # street: Optional[str] = None
    # city: Optional[str] = None
    # county: Optional[str] = None
    # state: Optional[str] = None
    # country: Optional[str] = None
    # postalcode: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    radius: int = 0
    max_results: Optional[int] = 3
