from typing import Literal

from pydantic import BaseModel


class ThreadMessagesCreate(BaseModel):
    thread_id: str
    content: str
    role: Literal["user"] = "user"
    file_ids: list[str] | None = None
    metadata: object | None = None


class ThreadMessagesRetrieve(BaseModel):
    message_id: str
    thread_id: str


class ThreadMessageUpdate(BaseModel):
    message_id: str
    thread_id: str
    metadata: object | None = None


class ThreadMessageList(BaseModel):
    thread_id: str
    after: str | None = None
    before: str | None = None
    limit: int | None = None
    order: Literal["asc", "desc"] | None = None


class ThreadMessageFileRetrieve(BaseModel):
    file_id: str
    thread_id: str
    message_id: str


class ThreadMessageFileList(BaseModel):
    thread_id: str
    message_id: str
    after: str | None = None
    before: str | None = None
    limit: int | None = None
    order: Literal["asc", "desc"] | None = None

