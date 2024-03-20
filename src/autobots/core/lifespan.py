from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from src.autobots.action_graph.scheduler.scheduler import Scheduler
from src.autobots.core.logging.setup_logger import setup_logger
from src.autobots.core.database.mongo_base import close_mongo_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger()
    Scheduler.start()
    logger.info("starting server")
    yield
    logger.info("Clean up and release the resources")
    Scheduler.stop()
    close_mongo_client()
    logger.info("stopping server")
