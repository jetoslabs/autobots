from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.autobots.action.action.action_doc_model import ActionDoc
from src.autobots.conn.openai.openai_chat.chat_model import Message
from src.autobots.data_model.updated_at import UpdatedAt


class ChatFind(BaseModel):
    id: Optional[str] = Field(default=None)
    title: Optional[str] = None
    created_at: Optional[datetime] = None


class ChatDocFind(ChatFind):
    user_id: str


class ChatUpdate(BaseModel):
    title: Optional[str] = None
    messages: Optional[List[Message]]


class ChatDocUpdate(ChatUpdate):
    id: str
    user_id: str


class ChatCreate(BaseModel):
    action: ActionDoc
    messages: List[Message]


class ChatDocCreate(ChatCreate, UpdatedAt):
    title: Optional[str]
    user_id: str
    created_at: datetime = datetime.now()


class ChatDoc(ChatDocCreate):
    __collection__ = "Chats"

    id: str = Field(..., alias='_id')
