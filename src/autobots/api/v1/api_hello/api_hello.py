from fastapi import APIRouter

from src.autobots import SettingsProvider

router = APIRouter(prefix=SettingsProvider.sget().API_Hello, tags=[SettingsProvider.sget().API_Hello])


@router.get("/")
async def hello():
    return {"hello": "world"}
