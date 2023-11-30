import uvicorn
from ddtrace import patch
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from autobots import SettingsProvider
from autobots.api.ui import ui
from autobots.api.v1 import v1
from autobots.core.fastapi_desc import FastAPIDesc
from autobots.core.lifespan import lifespan
from autobots.subscription.api_usage_dispatch import usage_info_dispatch

patch(fastapi=True)
app = FastAPI(lifespan=lifespan, **FastAPIDesc().model_dump())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(BaseHTTPMiddleware, dispatch=usage_info_dispatch)


app.include_router(v1.router)
app.include_router(router=v1.router_docs)
app.include_router(router=ui.router)

if __name__ == "__main__":
    SettingsProvider.set()
    settings = SettingsProvider.sget()
    # Run server
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True,
        log_level="debug",
        workers=3,
    )
