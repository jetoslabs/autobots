from fastapi import APIRouter, HTTPException
from loguru import logger

from src.autobots import SettingsProvider

router = APIRouter(prefix=SettingsProvider.sget().API_Hello, tags=[SettingsProvider.sget().API_Hello])


@router.get("/")
async def hello():
    return {"hello": "world"}


@router.get("/test_exception")
async def test_exception(catch_exception: bool = False):
    if catch_exception:
        try:
            return 1 / 0
        except ZeroDivisionError:
            logger.exception("Zero division error")
            raise HTTPException(status_code=400, detail="Zero division errorsss")
    else:
        return 1 / 0
