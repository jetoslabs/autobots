from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class AppMetadata(BaseModel):
    provider: str
    providers: List[str]


class UserMetadata(BaseModel):
    address: Optional[str]
    avatar_url: Optional[str]
    email: Optional[str]
    email_verified: Optional[bool]
    full_name: Optional[str]
    iss: Optional[str]
    name: Optional[str]
    picture: Optional[str]
    provider_id: Optional[str]
    sub: Optional[str]


class Amr(BaseModel):
    method: str
    timestamp: int


class SupaJwtPayload(BaseModel):
    aud: str
    exp: int
    sub: str
    email: str
    phone: Optional[str] = ""
    app_metadata: AppMetadata
    user_metadata: UserMetadata | dict
    role: str
    aal: str
    amr: List[Amr]
    session_id: str


class JwtPayload(SupaJwtPayload):
    pass


class BearerAccessToken(BaseModel):
    access_token: str  # access_token is jwt
    token_type: str


class AccessTokenSchema(BaseModel):
    iss: str
    exp: datetime
    sub: str
    aud: str
    user_id: str
    email: str
    scopes: List[str] | None
