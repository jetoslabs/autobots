import uvicorn
from fastapi import FastAPI

from autobots.api.v1 import v1
from autobots.core.lifespan import lifespan
from autobots.core.settings import settings

app = FastAPI(lifespan=lifespan)
app.include_router(v1.router)

if __name__ == "__main__":
    # Run server
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_RELOAD,
        log_level=settings.APP_LOG_LEVEL,
        workers=settings.APP_WORKERS
    )
