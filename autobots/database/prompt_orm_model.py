from fastapi.encoders import jsonable_encoder
from sqlalchemy import Column, UUID, text, func, DateTime, String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from autobots.conn.openai.chat import ChatReq
from autobots.database.base import Base
from autobots.database.target_platform import LLMTargetPlatform


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
