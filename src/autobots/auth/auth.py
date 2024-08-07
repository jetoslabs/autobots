from functools import lru_cache

import gotrue
from fastapi import HTTPException
from gotrue import UserAttributes
from pydantic import EmailStr, HttpUrl

from src.autobots.conn.supabase.supabase import Supabase, get_supabase


class Auth:

    def __init__(self, supabase: Supabase = get_supabase()):
        self.supabase_client = supabase.client

    async def sign_in_with_password(self, email: EmailStr, password: str) -> gotrue.AuthResponse:
        res: gotrue.AuthResponse = self.supabase_client.auth.sign_in_with_password({"email": email, "password": password})
        user: gotrue.User | None = res.user
        session: gotrue.Session | None = res.session

        if not user or not session:
            raise HTTPException(status_code=401, detail="User Session not found")

        return res

    async def sign_up_with_password(
            self, email: EmailStr, password: str, redirect_to: None | EmailStr = None
    ) -> gotrue.AuthResponse:
        credentials = {"email": email, "password": password}
        if redirect_to:
            credentials["options"] = {"redirect_to": redirect_to}
        res: gotrue.AuthResponse = self.supabase_client.auth.sign_up(credentials)
        if not res.user:
            raise HTTPException(status_code=409, detail="System conflict while creating user")
        return res

    async def reset_password_email(self, email: EmailStr, redirect_to: HttpUrl = None) -> bool:
        options = {}
        if redirect_to:
            options["redirect_to"] = redirect_to
        self.supabase_client.auth.reset_password_email(email=email, options=options)
        return True

    async def refresh_session(self, refresh_token: str) -> gotrue.AuthResponse:
        res: gotrue.AuthResponse = self.supabase_client.auth.refresh_session(refresh_token=refresh_token)
        return res

    async def sign_out(self) -> None:
        self.supabase_client.auth.sign_out()

    async def update_user(self, attributes: UserAttributes) -> gotrue.UserResponse:
        user = self.supabase_client.auth.update_user(attributes=attributes)
        return user



@lru_cache
def get_auth(supabase: Supabase = get_supabase()) -> Auth:
    return Auth(supabase)
