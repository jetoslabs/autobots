from enum import Enum
from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator

from src.autobots.conn.duckduckgo.duckduckgo_region_model import Region


# class Safesearch(str, Enum):
#     on = "on"
#     moderate = "moderate"
#     off = "off"


class Timelimit(str, Enum):
    all = "all"
    d = "day"
    w = "week"
    m = "month"
    y = "year"


class SearchTextParams(BaseModel):
    keywords: str = ""
    region: Region = Region.wt_wt
    safesearch: Literal["on", "moderate", "off"] = "moderate"
    timelimit: Timelimit | None = None
    max_results: int = Field(3, ge=1, le=10)

    @field_validator("region", "timelimit")
    @classmethod
    def get_enum_name(cls, value):
        if isinstance(value, Enum):
            if isinstance(value, Timelimit):
                if value == Timelimit.all:
                    return None
            return value.value
        return value


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


class LicenseImage(str, Enum):
    All_Creative_Commons = "any"
    Public_Domain = "Public"
    Free_to_Share_and_Use = "Share"
    Free_to_Share_and_Use_Commercially = "ShareCommercially"
    Free_to_Modify_Share_and_Use = "Modify"
    Free_to_Modify_Share_and_Use_Commercially = "ModifyCommercially"


class SearchImageParams(BaseModel):
    keywords: str = ""
    region: Region = Region.wt_wt
    safesearch: Literal["on", "moderate", "off"] = "moderate"
    timelimit: Literal["Day", "Week", "Month", "Year"] | None = None
    size: Literal["Small", "Medium", "Large", "Wallpaper"] | None = None
    color: Literal[
               "color", "Monochrome", "Red", "Orange", "Yellow", "Green", "Blue", "Purple", "Pink", "Brown", "Black", "Gray", "Teal", "White"] | None = None
    type_image: Literal["photo", "clipart", "gif", "transparent", "line"] | None = None
    layout: Literal["Square", "Tall", "Wide"] | None = None
    license_image: LicenseImage | None = None
    max_results: int = Field(3, ge=1, le=10)

    @field_validator("region")#, "license_image")
    @classmethod
    def get_enum_name(cls, value):
        if isinstance(value, Enum):
            return value.name
        return value


class SearchVideoParams(BaseModel):
    keywords: str = ""
    region: Region = Region.wt_wt
    safesearch: Literal["on", "moderate", "off"] = "moderate"
    timelimit: Literal["Day", "Week", "Month", "Year"] | None = None
    resolution: Literal["high", "standard"] | None = None
    duration: Literal["short", "medium", "long"] | None = None
    license_videos: Literal["creativeCommon", "youtube"] | None = None
    max_results: int = Field(3, ge=1, le=10)

    @field_validator("region")
    @classmethod
    def get_enum_name(cls, value):
        if isinstance(value, Enum):
            return value.name
        return value
