from contextlib import asynccontextmanager

import uvicorn
from ddtrace import patch
from fastapi import FastAPI

from autobots.api.v1 import v1
from autobots.core.log import log
from autobots.core.settings import get_settings
from autobots.database.mongo_base import close_mongo_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    log.info("Clean up and release the resources")
    close_mongo_client()


patch(fastapi=True)
app = FastAPI(lifespan=lifespan)
app.include_router(v1.router)

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
