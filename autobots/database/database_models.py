from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy import Column, String, Date, UUID, ForeignKey, DateTime, func, text
from sqlalchemy.dialects.postgresql import JSONB

from autobots.conn.openai.chat import Message
from autobots.database.base import Base


class UserORM(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())

    def __init__(self, id: UUID):
        self.id = id


class PromptORM(Base):
    __tablename__ = "prompts"

    id = Column(UUID(as_uuid=True), server_default=text("gen_random_uuid()"), primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    name = Column(String)
    description = Column(String, default='')
    prompt = Column(JSONB)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    target_platform = Column(String)

    def __init__(self, name: str, prompt: List[Message], user_id: UUID, target_platform: str, description: str = None):
        self.name = name
        self.description = description
        self.prompt = jsonable_encoder(prompt)
        self.user_id = user_id
        self.target_platform = target_platform
