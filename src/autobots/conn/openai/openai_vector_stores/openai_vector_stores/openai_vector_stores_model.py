from typing import List, Dict, Literal

from openai.types.beta import vector_store_create_params
from pydantic import BaseModel, Field


class CreateVectorStore(BaseModel):
    file_ids: List[str] | None = None
    name: str | None = None
    expires_after: vector_store_create_params.ExpiresAfter | None = None
    metadata: Dict[str, str] | None = None


class ListVectorStore(BaseModel):
    limit: int | None = Field(None, ge=1, le=100)
    order: Literal['desc', 'asc'] | None = Field(None)
    after: str | None = None
    before: str | None = None


class RetrieveVectorStore(BaseModel):
    vector_store_id: str


class UpdateVectorStore(BaseModel):
    vector_store_id: str
    name: str | None = None
    after: str | None = None
    before: str | None = None


class DeleteVectorStore(BaseModel):
    vector_store_id: str

