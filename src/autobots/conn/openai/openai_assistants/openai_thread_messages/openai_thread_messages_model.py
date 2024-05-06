from typing import Literal, Iterable

from openai.types.beta.threads import message_create_params
from pydantic import BaseModel


class ThreadMessagesCreate(BaseModel):
    thread_id: str
    role: Literal["user", "assistant"] = "user"
    content: str
    attachments: Iterable[message_create_params.Attachment] | None = None
    metadata: object | None = None


class ThreadMessagesRetrieve(BaseModel):
    thread_id: str
    message_id: str


class ThreadMessageUpdate(BaseModel):
    thread_id: str
    message_id: str
    metadata: object | None = None


class ThreadMessageList(BaseModel):
    thread_id: str
    limit: int | None = None
    order: Literal["asc", "desc"] | None = None
    after: str | None = None
    before: str | None = None
    run_id: str | None = None


class ThreadMessageDelete(BaseModel):
    thread_id: str
    message_id: str


# class ThreadMessageFileRetrieve(BaseModel):
#     file_id: str
#     thread_id: str
#     message_id: str


# class ThreadMessageFileList(BaseModel):
#     thread_id: str
#     message_id: str
#     after: str | None = None
#     before: str | None = None
#     limit: int | None = None
#     order: Literal["asc", "desc"] | None = None
