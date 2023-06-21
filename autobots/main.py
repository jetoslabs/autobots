import uvicorn
from fastapi import FastAPI



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
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug",
        workers=1
    )
