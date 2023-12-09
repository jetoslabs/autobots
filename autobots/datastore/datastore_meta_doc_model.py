from datetime import datetime
from typing import Optional

from pydantic import Field, BaseModel


class DatastoreMetaFind(BaseModel):
    """
    base class to be utilized to find datastore_meta
    """
    id: Optional[str] = Field(default=None)  # , alias='_id')
    datastore_id: Optional[str] = None
    name: Optional[str] = None


class DatastoreMetaDocFind(DatastoreMetaFind):
    """
    Add in user id to enforce multi-tenancy
    """
    user_id: str


class DatastoreMetaUpdate(BaseModel):
    """
    base class to be utilized to update datastore_meta
    """
    name: Optional[str] = None


class DatastoreMetaDocUpdate(DatastoreMetaUpdate):
    """
    Add in user id to enforce multi-tenancy
    """
    user_id: str


class DatastoreMetaCreate(BaseModel):
    """
    base class to be utilized to create datastore_meta
    """
    name: str


class DatastoreMetaDocCreate(DatastoreMetaCreate):
    """
    Add in user id to enforce multi-tenancy
    """
    datastore_id: str
    user_id: str
    created_at: datetime = datetime.now()


class DatastoreMetaDoc(DatastoreMetaDocCreate):
    __collection__ = "DatastoreMetas"

    id: str = Field(..., alias='_id')

    class Config:
        populate_by_name = True
