from contextlib import asynccontextmanager

from fastapi import FastAPI

from autobots.core.log import log


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup work
    log.debug("starting server")
    yield
    # shutdown work
    log.debug("stopping server")
