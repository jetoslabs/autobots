from pydantic import BaseModel


class ZohoTokenRequest(BaseModel):
    api_key: str


class ZohoTokenGenerateRequest(BaseModel):
    api_domain: str
    client_id: str
    client_secret: str
    auth_code: str


class ZohoTokenGenerateResponse(BaseModel):
    access_token: str
    refresh_token: str
    api_domain: str
    token_type: str
    expires_in: int


class ZohoTokenRefreshRequest(BaseModel):
    api_domain: str
    client_id: str
    client_secret: str
    refresh_token: str


class ZohoTokenRefreshResponse(BaseModel):
    access_token: str
    api_domain: str
    token_type: str
    expires_in: int
