from fastapi import APIRouter

from autobots.api.v1 import hello, auth, api_prompts
from autobots.core.settings import get_settings

router = APIRouter(prefix=get_settings().API_v1)

router.include_router(hello.router, prefix=get_settings().API_Hello, tags=["hello"])
router.include_router(auth.router, prefix=get_settings().API_AUTH, tags=["auth"])
router.include_router(api_prompts.router, prefix=get_settings().API_PROMPTS, tags=["prompts"])
