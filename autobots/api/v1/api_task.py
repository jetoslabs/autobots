from typing import Any

from celery import result
from fastapi import APIRouter
from starlette.responses import JSONResponse

from autobots.worker import hello_task

router = APIRouter()


@router.post("/hello")
async def celery_hello(seconds: int) -> JSONResponse:
    task = hello_task.delay(seconds)
    return JSONResponse({"task_id": task.id})


@router.get("/{task_id}")
async def celery_hello(task_id: str) -> Any:
    task = result.AsyncResult(task_id)
    return task.result
