from enum import Enum
from typing import Optional, List
from pydantic import Field
from autobots import SettingsProvider
from pydantic import BaseModel, HttpUrl
from datetime import datetime
class DiscordReqModel(BaseModel):
    key: str = Field(default=SettingsProvider.sget().STABLE_DIFFUSION_API_KEY,
                     description="Your API Key used for request authorization.")
    prompt: str = Field(..., description="Text prompt with description of the things you want in the image to be generated.")

class DiscordChild(BaseModel):
    button: str
    jobid: str
    messageId: str


class DiscordAttachment(BaseModel):
    url: HttpUrl
    proxy_url: HttpUrl
    width: int
    height: int
    content_type: str
    id: str
    filename: str
    size: int
class DiscordJobsApiResponse(BaseModel):
    jobid: Optional[str]
    verb: Optional[str]
    status: Optional[str]
    created: Optional[datetime]
    updated: Optional[datetime]
    prompt: Optional[str]
    children: Optional[List[DiscordChild]]
    buttons: Optional[List[str]]
    discord: Optional[str]
    channel: Optional[str]
    server: Optional[str]
    maxJobs: Optional[int]
    messageId: Optional[str]
    content: Optional[str]
    timestamp: Optional[datetime]
    attachments: Optional[List[DiscordAttachment]]
    code: int
    message: Optional[str]

    class Config:
        allow_population_by_field_name = True  # This allows extra fields in the response


class DiscordErrorResponse(BaseModel):
    error: str
    code: int


class DiscordImagineApiResponse(BaseModel):
    jobid: Optional[str]
    verb: Optional[str]
    status: Optional[str]
    created: Optional[datetime]
    updated: Optional[datetime]
    prompt: Optional[str]
    discord: Optional[str]
    channel: Optional[str]
    server: Optional[str]
    maxJobs: Optional[int]
    replyUrl: Optional[HttpUrl]
    replyRef: Optional[str]
    messageId: Optional[str]
    content: Optional[str]
    timestamp: Optional[datetime]
    message: Optional[str]
    code: int
    class Config:
        allow_population_by_field_name = True  # This allows extra fields in the response