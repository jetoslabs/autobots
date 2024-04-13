from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from src.autobots.action_graph.schedule.schedule import Schedule
from src.autobots.core.logging.loguru_handler import replace_logging_with_loguru
from src.autobots.core.logging.setup_logger import setup_logger
from src.autobots.core.database.mongo_base import close_mongo_client, close_pymongo_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting server")
    setup_logger()
    replace_logging_with_loguru()
    Schedule.start_scheduler()
    logger.info("Server started")

    yield

    logger.info("Stopping server")
    logger.info("Clean up and release the resources")
    Schedule.stop_scheduler()
    close_mongo_client()
    close_pymongo_client()
    logger.info("Server stopped")

