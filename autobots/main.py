import uvicorn
from fastapi import FastAPI

from autobots.core.settings import settings

app = FastAPI()


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # startup work
#     settings = Settings()
#     await resource.set_settings(settings=settings)
#     yield
#     # shutdown work


@app.get("/")
async def hello():
    return {"hello": "settings.APP_HOST"}


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
