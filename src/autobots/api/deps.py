# from typing import Generator
#
# from sqlalchemy.orm import Session
#
# from autobots.database import base
#
from fastapi import Request
from gotrue import UserResponse

from src.autobots.auth.security import get_user_from_access_token


# def get_db() -> Generator[Session, None, None]:
#     return base.get_db()


async def get_user_from_cookie(request: Request) -> UserResponse | None:
    token = request.cookies.get("Authorization")
    if not token:
        return None
    user = get_user_from_access_token(
        api_key_query=None, api_key_header=None, api_key_cookie=token
    )
    if not user:
        return None
    return user
