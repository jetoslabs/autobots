import os
import time

from celery import Celery, shared_task

from autobots.core.log import log

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


@shared_task
def hello_task(seconds: int):
    log.info("hello_task")
    time.sleep(int(seconds))
    return {"hello": "distributed world"}
