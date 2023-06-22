import uvicorn
from fastapi import FastAPI

from autobots.api.v1 import v1
from autobots.core.lifespan import lifespan
from autobots.core.settings import get_settings

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
