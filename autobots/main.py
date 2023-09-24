from contextlib import asynccontextmanager
import uvicorn
from ddtrace import patch
from fastapi import FastAPI, APIRouter
from autobots.api.v1 import v1
from autobots.api.v1.ads.google import google_auth
from autobots.core.log import log
from autobots.core.settings import get_settings
from autobots.database.mongo_base import close_mongo_client
from fastapi.staticfiles import StaticFiles
import aiofiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    log.info("Clean up and release the resources")
    close_mongo_client()

patch(fastapi=True)

# New root router   
root_router = APIRouter()
root_router.include_router(google_auth.router, tags=["google_ads_auth"]) 

app = FastAPI(lifespan=lifespan)
app.include_router(root_router)  # Include the root router
app.include_router(v1.router)

app.mount("/static", StaticFiles(directory="autobots/static"), name="static")

@app.get("/")
async def serve_root():
    return await aiofiles.open("autobots/static/google/index.html", mode="r").read()


if __name__ == "__main__":
    # Run server
    uvicorn.run(
        "main:app",
        host=get_settings().APP_HOST,
        port=get_settings().APP_PORT,
        reload=get_settings().APP_RELOAD,
        log_level=get_settings().APP_LOG_LEVEL,
        workers=get_settings().APP_WORKERS
    )
