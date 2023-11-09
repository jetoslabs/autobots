from enum import Enum
from typing import Optional, Union, Literal

from pydantic import BaseModel


class ImageSize(str, Enum):
    size_256x256 = "256x256"
    size_512x512 = "512x512"
    size_1024x1024 = "1024x1024"


class ResponseFormat(str, Enum):
    url = "url"
    b64_json = "b64_json"


# class ImageReq(BaseModel):
#     prompt: str = ""
#     n: int = 1
#     size: ImageSize = ImageSize.size_1024x1024
#     response_format: ResponseFormat = ResponseFormat.url
#     user: str = ""

class ImageReq(BaseModel):
    prompt: str
    model: Literal["dall-e-3"] = "dall-e-3"
    n: Optional[int] = 1
    quality: Literal["standard", "hd"] = "standard"
    response_format: Optional[Literal["url", "b64_json"]] = "url"
    size: Optional[Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"]] = "1024x1024"
    style: Optional[Literal["vivid", "natural"]] = "natural"
    user: str = ""
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    # extra_headers: Headers | None = None,
    # extra_query: Query | None = None,
    # extra_body: Body | None = None,
    # timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,


# class ImageRes(BaseModel):
#     url: Optional[str] = None
#     b64_json: Optional[str] = None

