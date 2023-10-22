from fastapi import APIRouter

from autobots.core.log import log

router = APIRouter()


@router.get("/")
async def hello():
    return {"hello": "world"}
