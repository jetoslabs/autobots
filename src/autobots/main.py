import uvicorn
from ddtrace import patch
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.autobots import SettingsProvider
from src.autobots.api.ui import ui
from src.autobots.api.v1 import v1
from src.autobots.core.fastapi_desc import FastAPIDesc
from src.autobots.core.lifespan import lifespan
from src.autobots.middleware.api_usage_dispatch import usage_info_dispatch
from src.autobots.middleware.dispatch_catch_all_exception import catch_all_exception_dispatch
from src.autobots.middleware.middleware_add_context import add_context_dispatch

patch(fastapi=True)
app = FastAPI(lifespan=lifespan, **FastAPIDesc().model_dump())

app.mount("/static", StaticFiles(directory="src/autobots/ui/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(BaseHTTPMiddleware, dispatch=usage_info_dispatch)
app.add_middleware(BaseHTTPMiddleware, dispatch=catch_all_exception_dispatch)
app.add_middleware(BaseHTTPMiddleware, dispatch=add_context_dispatch)

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
