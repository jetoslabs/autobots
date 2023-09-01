from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ImageSize(str, Enum):
    size_256x256 = "256x256"
    size_512x512 = "512x512"
    size_1024x1024 = "1024x1024"


class ResponseFormat(str, Enum):
    url = "url"
    b64_json = "b64_json"


class ImageReq(BaseModel):
    prompt: str = ""
    n: int = 1
    size: ImageSize = ImageSize.size_1024x1024
    response_format: ResponseFormat = ResponseFormat.url
    user: str = ""


class ImageRes(BaseModel):
    url: Optional[str] = None
    b64_json: Optional[str] = None

