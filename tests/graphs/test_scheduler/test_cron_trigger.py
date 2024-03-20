import time

import pytest
from loguru import logger

from src.autobots.action.action.common_action_models import TextObj
from src.autobots.action_graph.scheduler.scheduler import Scheduler
from src.autobots.action_graph.scheduler.trigger import CronTrigger


class MockAction():
    async def run_async(self, text_obj: TextObj):
        logger.info(text_obj.text)
        return "ok"


@pytest.mark.asyncio
async def test_cron_trigger_happy_path(set_test_settings):
    Scheduler.start()
    text_obj = TextObj(text=f"xyz+{time.time()}")
    job = Scheduler.add_scheduled_action_graph(
        MockAction().run_async,
        # trigger=IntervalTrigger(seconds=300),
        trigger=CronTrigger(minute="*/2"),
        kwargs={
            "text_obj": text_obj.model_dump(exclude_none=True)
        }
    )
    jobs = Scheduler._scheduler.get_jobs()
    assert len(jobs) == 1
    assert jobs[0] == job
    Scheduler.stop()
    assert True
