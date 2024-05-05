from typing import Literal, List

from pydantic import BaseModel, Field


class CreateVectorStoreFileBatch(BaseModel):
    vector_store_id: str
    file_ids: List[str]


class ListVectorStoreFilesInBatch(BaseModel):
    vector_store_id: str
    batch_id: str
    limit: int | None = Field(None, ge=1, le=100)
    order: Literal['desc', 'asc'] | None = Field(None)
    after: str | None = None
    before: str | None = None
    filter: Literal['in_progress', 'completed', 'failed', 'cancelled'] | None = None


class RetrieveVectorStoreFileBatch(BaseModel):
    vector_store_id: str
    batch_id: str


class CancelVectorStoreFileBatch(BaseModel):
    vector_store_id: str
    batch_id: str
