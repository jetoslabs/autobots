from fastapi import APIRouter

from autobots.api.v1 import hello
from autobots.core.settings import settings

router = APIRouter(prefix=settings.API_v1)

router.include_router(hello.router, prefix=settings.API_Hello)
