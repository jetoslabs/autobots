from fastapi.encoders import jsonable_encoder
from sqlalchemy import Column, String, UUID, ForeignKey, DateTime, func, text, Float
from sqlalchemy.dialects.postgresql import JSONB

from autobots.conn.openai.chat import ChatReq
from autobots.database.base import Base
from autobots.database.target_platform import LLMTargetPlatform


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
    version = Column(Float)
    description = Column(String, default='')
    chat_req = Column(JSONB)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    target_platform = Column(String)

    def __init__(
            self, name: str, chat_req: ChatReq, user_id: UUID, target_platform: LLMTargetPlatform,
            version: float = 1, description: str = ""
    ):
        self.name = name
        self.version = version
        self.description = description
        self.chat_req = jsonable_encoder(chat_req)
        self.user_id = user_id
        self.target_platform = target_platform


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
