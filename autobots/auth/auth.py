from functools import lru_cache

import gotrue
from fastapi import HTTPException
from pydantic import EmailStr

from autobots.conn.supabase.supabase import Supabase, get_supabase


class Auth:

    def __init__(self, supabase: Supabase = get_supabase()):
        self.supabase_client = supabase.client

    def sign_in_with_password(self, email: EmailStr, password: str) -> gotrue.AuthResponse:
        res: gotrue.AuthResponse = self.supabase_client.auth.sign_in_with_password({"email": email, "password": password})
        user: gotrue.User | None = res.user
        session: gotrue.Session | None = res.session

        if not user or not session:
            raise HTTPException(status_code=401, detail="User Session not found")

        return res

    def sign_up_with_password(self, email: EmailStr, password: str) -> gotrue.AuthResponse:
        res: gotrue.AuthResponse = self.supabase_client.auth.sign_up({"email": email, "password": password})
        if not res.user:
            raise HTTPException(status_code=409, detail="System conflict while creating user")
        return res


@lru_cache
def get_auth(supabase: Supabase = get_supabase()) -> Auth:
    return Auth(supabase)
