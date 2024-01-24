from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.autobots.core.logging.setup_logger import setup_logger
from src.autobots.core.database.mongo_base import close_mongo_client
from src.autobots.core.logging.log import Log


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger()
    Log.info("starting server")
    yield
    Log.info("Clean up and release the resources")
    close_mongo_client()
    Log.info("stopping server")
