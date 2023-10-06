import gotrue
from fastapi import APIRouter, Depends
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from starlette.responses import JSONResponse

from autobots.api.v1 import v1
from autobots.auth.security import get_user_from_access_token
from autobots.core.fastapi_desc import FastAPIDesc
from autobots.core.settings import get_settings

router = APIRouter()


@router.get("/openapi.json")
async def open_api_json(user_res: gotrue.UserResponse = Depends(get_user_from_access_token)):
    fastapi_dec = FastAPIDesc()
    return JSONResponse(get_openapi(
        title=fastapi_dec.title,
        version=fastapi_dec.version,
        description=fastapi_dec.description,
        routes=v1.router.routes,
        contact=fastapi_dec.contact,
        license_info=fastapi_dec.license_info
    ))


@router.get("/docs")
async def api_docs(user_res: gotrue.UserResponse = Depends(get_user_from_access_token)):
    return get_swagger_ui_html(openapi_url=f"{get_settings().API_v1}/openapi.json", title="docs")


@router.get("/redoc")
async def api_docs(user_res: gotrue.UserResponse = Depends(get_user_from_access_token)):
    return get_redoc_html(openapi_url=f"{get_settings().API_v1}/openapi.json", title="redoc")
