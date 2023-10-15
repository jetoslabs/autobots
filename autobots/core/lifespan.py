from contextlib import asynccontextmanager

from fastapi import FastAPI

from autobots.core.log import log, setup_logger
from autobots.core.settings import SettingsProvider
from autobots.database.mongo_base import close_mongo_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger()
    log.info("starting server")
    yield
    log.info("Clean up and release the resources")
    close_mongo_client()
    log.info("stopping server")
