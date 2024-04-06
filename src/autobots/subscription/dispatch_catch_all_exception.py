from loguru import logger
from requests import Request
from starlette.responses import JSONResponse


async def catch_all_exception_dispatch(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            status_code=500,
            content={
                'detail': str(e)
            }
        )
