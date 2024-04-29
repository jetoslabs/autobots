from typing import Optional, List
from pydantic import Field, ConfigDict
from src.autobots import SettingsProvider
from pydantic import BaseModel, HttpUrl
from datetime import datetime


class DiscordReqModel(BaseModel):
    prompt: Optional[str] = Field("", description="Text prompt with description of the things" +
                                                  " you want in the image to be generated.")
    job_id: Optional[str] = Field(default="", description="Job id to fetch")
    button: Optional[str] = Field(default="", description="Button to run the action")


class DiscordJobReqModel(BaseModel):
    useapi_net_endpoint_url: str = Field(default=SettingsProvider.sget().USEAPI_NET_END_POINT_URL,
                                         description="USE_API end point")
    use_api_net_token: str = Field(default=SettingsProvider.sget().USEAPI_NET_TOKEN,
                                   description="Your discord channel id used for request authorization.")
    job_id: str = Field(description="Job id to fetch")


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
    prompt: Optional[str] = None
    button: Optional[str] = None
    children: Optional[List[DiscordChild]] = None
    buttons: Optional[List[str]] = None
    discord: Optional[str]
    channel: Optional[str]
    server: Optional[str]
    maxJobs: Optional[int]
    messageId: Optional[str]
    replyUrl: Optional[str] = None
    replyRef: Optional[str] = None
    content: Optional[str]
    timestamp: Optional[datetime]
    attachments: Optional[List[DiscordAttachment]] = None
    code: int
    message: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)  # This allows extra fields in the response


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
    replyUrl: Optional[HttpUrl] = None
    replyRef: Optional[str] = None
    messageId: Optional[str] = None
    content: Optional[str]
    timestamp: Optional[datetime]
    message: Optional[str] = None
    code: int

    model_config = ConfigDict(populate_by_name=True)  # This allows extra fields in the response


class DiscordButtonJobResponse(BaseModel):
    jobid: Optional[str]
    verb: Optional[str]
    status: Optional[str]
    created: Optional[datetime]
    updated: Optional[datetime]
    describeUrl: Optional[str] = None
    discord: Optional[str]
    channel: Optional[str]
    server: Optional[str]
    maxJobs: Optional[int] = None
    replyUrl: Optional[str] = None
    replyRef: Optional[str] = None
    messageId: Optional[str] = None
    content: Optional[str]
    timestamp: Optional[datetime]
    error: Optional[str] = None
    errorDetails: Optional[str] = None
    executingJobs: Optional[dict] = None
    code: Optional[int]

    model_config = ConfigDict(populate_by_name=True)  # This allows extra fields in the response
