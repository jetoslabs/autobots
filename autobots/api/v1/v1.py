from fastapi import APIRouter

from autobots.api.v1 import hello
from autobots.core.settings import get_settings

router = APIRouter(prefix=get_settings().API_v1)

router.include_router(hello.router, prefix=get_settings().API_Hello)
