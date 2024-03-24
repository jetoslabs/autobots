import datetime
from typing import Any, List

from apscheduler.job import Job
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers import SchedulerAlreadyRunningError, SchedulerNotRunningError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.util import undefined
from loguru import logger

from src.autobots import SettingsProvider
from src.autobots.action_graph.schedule.trigger import Trigger
from src.autobots.core.database.mongo_base import get_mongo_client


class Schedule:
    JOBSTORE = "default" # 'default' is the default jobstore, if env var, then remove all jobstores before adding this one
    EXECUTOR = "default"
    _scheduler: AsyncIOScheduler | None = None

    def create_schedule(
            self,
            func: Any,
            trigger: Trigger,
            args: list | tuple = None,
            kwargs: dict = None,
            id: str = None,
            name: str = None,
            misfire_grace_time: int = undefined,
            coalesce: bool = undefined,
            max_instances: int = undefined,
            next_run_time: datetime = undefined,
            jobstore: str = JOBSTORE,
            executor: str = EXECUTOR,
            replace_existing: bool = False,
    ) -> Job:
        job = Schedule._scheduler.add_job(
            func=func,
            **trigger.model_dump(exclude_none=True),
            args=args,
            kwargs=kwargs,
            id=id,
            name=name,
            misfire_grace_time=misfire_grace_time,
            coalesce=coalesce,
            max_instances=max_instances,
            next_run_time=next_run_time,
            jobstore=jobstore,
            executor=executor,
            replace_existing=replace_existing
        )
        return job

    def modify_schedule(
            self,
            job_id: str,
            **changes
    ) -> Job:
        job = Schedule._scheduler.modify_job(
            job_id=job_id,
            **changes
        )
        return job

    def get_schedule(self, job_id: str, jobstore: str = None) -> Job:
        job = Schedule._scheduler.get_job(job_id, jobstore)
        return job

    def list_schedule(self, jobstore: str = None) -> List[Job]:
        jobs = Schedule._scheduler.get_jobs(jobstore)
        return jobs

    def delete_schedule(self, job_id: str, jobstore: str = None) -> Any:
        job = Schedule._scheduler.remove_job(job_id, jobstore)
        return job

    @staticmethod
    def start_scheduler():
        if Schedule._scheduler is None:
            try:
                jobstores = {
                    # 'default' is the default jobstore, if env var, then remove all jobstores before adding this one
                    Schedule.JOBSTORE: MongoDBJobStore(
                        database=SettingsProvider().sget().MONGO_DATABASE,
                        collection=SettingsProvider().sget().SCHEDULE_JOBSTORE_MONGO_DB_COLLECTION_NAME,
                        client=get_mongo_client(),
                    )
                }
                Schedule._scheduler = AsyncIOScheduler(jobstores=jobstores)
                Schedule._scheduler.start()
            except SchedulerAlreadyRunningError | RuntimeError | Exception as e:
                logger.error(str(e))
                raise

    @staticmethod
    def stop_scheduler():
        try:
            Schedule._scheduler.shutdown(wait=True)
        except SchedulerNotRunningError as e:
            logger.error(str(e))
            raise
