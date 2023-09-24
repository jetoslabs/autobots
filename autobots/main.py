from contextlib import asynccontextmanager
import uvicorn
from ddtrace import patch
from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from autobots.api.v1 import v1
from autobots.api.v1.ads.google import google_auth
from autobots.core.log import log
from autobots.core.settings import get_settings
from autobots.database.mongo_base import close_mongo_client
from autobots.subscription.api_usage import usage_info
from fastapi.staticfiles import StaticFiles
import aiofiles

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    log.info("Clean up and release the resources")
    close_mongo_client()

patch(fastapi=True)


root_router = APIRouter()
root_router.include_router(google_auth.router, tags=["google_ads_auth"]) 

app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(BaseHTTPMiddleware, dispatch=usage_info)

app.include_router(root_router)  # Include the root router
app.include_router(v1.router)
app.mount("/static", StaticFiles(directory="autobots/static"), name="static")


@app.get("/")
async def serve_root():
    async with aiofiles.open("autobots/static/google/index.html", mode="r") as f:
        content = await f.read()
    return content

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
