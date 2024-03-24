import time

import pytest
from loguru import logger

from src.autobots.action.action.common_action_models import TextObj
from src.autobots.action_graph.schedule.schedule import Schedule
from src.autobots.action_graph.schedule.trigger import CronTrigger


class MockAction():
    async def run_async(self, text_obj: TextObj):
        logger.info(text_obj.text)
        return "ok"


@pytest.mark.asyncio
async def test_cron_trigger_happy_path(set_test_settings):
    Schedule.start_scheduler()

    try:
        jobs = Schedule().list_schedule()
        assert len(jobs) == 0

        text_obj = TextObj(text=f"xyz+{time.time()}")

        job1 = Schedule().create_schedule( # noqa F841
            MockAction().run_async,
            # trigger=IntervalTrigger(seconds=300),
            trigger=CronTrigger(minute="*/2"),
            kwargs={
                "text_obj": text_obj.model_dump(exclude_none=True)
            },
            name="job1"
        )

        job2 = Schedule().create_schedule(
            MockAction().run_async,
            # trigger=IntervalTrigger(seconds=300),
            trigger=CronTrigger(minute="*/2"),
            kwargs={
                "text_obj": text_obj.model_dump(exclude_none=True)
            },
            name="job2"
        )
        Schedule().modify_schedule(
            job2.id,
            kwargs={
                "text_obj": TextObj(text="modified job").model_dump(exclude_none=True)
            }
        )

        jobs = Schedule().list_schedule()
        assert len(jobs) == 2
        jobs_dict = {job.id: job for job in jobs}
        assert jobs_dict.get(job2.id).kwargs.get("text_obj").get("text") == "modified job"

        for job in jobs:
            Schedule().delete_schedule(job.id)
        jobs = Schedule().list_schedule()
        assert len(jobs) == 0

    finally:
        # Schedule.stop_scheduler()
        assert True
