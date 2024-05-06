from typing import Literal

from pydantic import BaseModel, Field


class CreateVectorStoreFile(BaseModel):
    vector_store_id: str
    file_id: str


class ListVectorStoreFiles(BaseModel):
    vector_store_id: str
    limit: int | None = Field(None, ge=1, le=100)
    order: Literal['desc', 'asc'] | None = Field(None)
    after: str | None = None
    before: str | None = None
    filter: Literal['in_progress', 'completed', 'failed', 'cancelled'] | None = None


class RetrieveVectorStoreFile(BaseModel):
    vector_store_id: str
    file_id: str


class DeleteVectorStoreFile(BaseModel):
    vector_store_id: str
    file_id: str
