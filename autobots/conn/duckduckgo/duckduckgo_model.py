from enum import Enum

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
