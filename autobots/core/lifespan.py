from contextlib import asynccontextmanager

from fastapi import FastAPI

from autobots.core.log import setup_logger
from autobots.core.database.mongo_base import close_mongo_client
from autobots.core.logging.log import Log


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger()
    Log.info("starting server")
    yield
    Log.info("Clean up and release the resources")
    close_mongo_client()
    Log.info("stopping server")
