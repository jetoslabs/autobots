import uuid
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import ForeignKey, Column, UUID, String, DateTime, func

from autobots.core.database.base import Base


class DatastoreMetaModel(BaseModel):
    id: str
    name: str
    user_id: uuid.UUID
    created_at: datetime


class DatastoreMetaORM(Base):
    __tablename__ = "datastore_meta"

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    name = Column(String, primary_key=True)
    id = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    def __init__(self, user_id: UUID, name: str, id: str):
        self.user_id = user_id
        self.name = name
        self.id = id
