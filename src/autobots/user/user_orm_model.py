from sqlalchemy import Column, UUID, DateTime, func

from src.autobots.core.database.base import Base


class UserORM(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())

    def __init__(self, id: UUID):
        self.id = id
