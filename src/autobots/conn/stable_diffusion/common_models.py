from enum import Enum
from typing import List, Optional

from pydantic import HttpUrl, BaseModel


class StableDiffusionResStatus(str, Enum):
    success = "success"
    processing = "processing"
    error = "error"
    failed = "failed"


class StableDiffusionRes(BaseModel):
    urls: Optional[List[HttpUrl]]
    fetch_url: HttpUrl | None = None


class YesNo(str, Enum):
    yes = "yes"
    no = "no"
