from typing import List

from pydantic import BaseModel


class EmbeddingReq(BaseModel):
    model: str = "text-embedding-ada-002"
    input: List[str] | str  # max char size is 8192
    user: str = ""


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
