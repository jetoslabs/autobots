from typing import List, Union, Literal

from pydantic import BaseModel


class EmbeddingReq(BaseModel):
    input: Union[str, List[str], List[int], List[List[int]]]
    model: Literal["text-embedding-ada-002"] = "text-embedding-ada-002"
    encoding_format: Literal["float", "base64"] = "float"
    user: str = ""
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    # extra_headers: Headers | None = None,
    # extra_query: Query | None = None,
    # extra_body: Body | None = None,
    # timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,


class EmbeddingData(BaseModel):
    object: str
    embedding: List[float]
    index: int


class Usage(BaseModel):
    prompt_tokens: int
    total_tokens: int


class EmbeddingRes(BaseModel):
    object: str
    data: List[EmbeddingData]
    model: str
    usage: Usage
