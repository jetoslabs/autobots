from typing import Dict, List

from fastapi.encoders import jsonable_encoder
from sqlalchemy import Column, UUID, text, DateTime, func, String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from autobots.database.base import Base


class GraphORM(Base):
    __tablename__ = "graphs"

    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    name = Column(String)
    version = Column(Float)
    description = Column(String, default='')
    graph = Column(JSONB)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    def __init__(
            self, name: str, graph: Dict[str, List[str]], user_id: UUID,
            version: float = 1, description: str = ""
    ):
        self.name = name
        self.version = version
        self.description = description
        self.graph = jsonable_encoder(graph)
        self.user_id = user_id
