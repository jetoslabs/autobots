from typing import Optional, List
from pydantic import Field
from src.autobots import SettingsProvider
from pydantic import BaseModel, HttpUrl
from datetime import datetime


class DiscordReqModel(BaseModel):
    discord_server_id: Optional[str] = Field(default=SettingsProvider.sget().DISCORD_SERVER_ID,
                     description="Your discord server id used for request authorization.")
    prompt: Optional[str] = Field(..., description="Text prompt with description of the things" +
                                         " you want in the image to be generated.")
    useapi_net_endpoint_url: Optional[str] =  Field(default=SettingsProvider.sget().USEAPI_NET_END_POINT_URL,
                     description="USE_API end point")
    discord_token: Optional[str] = Field(default=SettingsProvider.sget().DISCORD_TOKEN,
                     description="Your discord token used for request authorization.")
    discord_channel_id: Optional[str] = Field(default=SettingsProvider.sget().DISCORD_CHANNEL_ID,
                               description="Your discord channel id used for request authorization.")
    use_api_net_token: Optional[str] = Field(default=SettingsProvider.sget().USEAPI_NET_TOKEN,
                               description="Your use aoi net token id used for request authorization.")
    job_id: Optional[str] = Field(default=None, description="Job id to fetch")
class DiscordJobReqModel(BaseModel):
   useapi_net_endpoint_url: str =  Field(default=SettingsProvider.sget().USEAPI_NET_END_POINT_URL,
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
        populate_by_name = True  # This allows extra fields in the response


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

    class Config:
        populate_by_name = True  # This allows extra fields in the response