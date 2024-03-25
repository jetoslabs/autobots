# import datetime
# from typing import Any
#
# from apscheduler.job import Job
# from apscheduler.schedulers import SchedulerAlreadyRunningError, SchedulerNotRunningError
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.util import undefined
# from loguru import logger
#
# from src.autobots.action_graph.schedule.trigger import Trigger
#
# class Scheduler():
#     _scheduler = AsyncIOScheduler()
#
#     @staticmethod
#     def add_schedule(
#             func: Any,
#             trigger: Trigger,
#             args: list | tuple = None,
#             kwargs: dict = None,
#             id: str = None,
#             name: str = None,
#             misfire_grace_time: int = undefined,
#             coalesce: bool = undefined,
#             max_instances: int = undefined,
#             next_run_time: datetime = undefined,
#             jobstore: str = 'default',
#             executor: str = 'default',
#             replace_existing: bool = False
#     ) -> Job:
#         job = Scheduler._scheduler.add_job(
#             func=func,
#             **trigger.model_dump(exclude_none=True),
#             args=args,
#             kwargs=kwargs,
#             id=id,
#             name=name,
#             misfire_grace_time=misfire_grace_time,
#             coalesce=coalesce,
#             max_instances=max_instances,
#             next_run_time=next_run_time,
#             jobstore=jobstore,
#             executor=executor,
#             replace_existing=replace_existing
#         )
#         return job
#
#     @staticmethod
#     def modify_schedule(
#             job_id: str,
#             func: Any,
#             trigger: Trigger,
#             args: list | tuple = None,
#             kwargs: dict = None,
#             id: str = None,
#             name: str = None,
#             misfire_grace_time: int = undefined,
#             coalesce: bool = undefined,
#             max_instances: int = undefined,
#             next_run_time: datetime = undefined,
#             jobstore: str = 'default',
#             executor: str = 'default',
#             replace_existing: bool = False
#     ) -> Job:
#         job = Scheduler._scheduler.modify_job(
#             job_id=job_id,
#             jobstore=jobstore,
#             func=func,
#             **trigger.model_dump(exclude_none=True),
#             args=args,
#             kwargs=kwargs,
#             id=id,
#             name=name,
#             misfire_grace_time=misfire_grace_time,
#             coalesce=coalesce,
#             max_instances=max_instances,
#             next_run_time=next_run_time,
#             executor=executor,
#             replace_existing=replace_existing
#         )
#         return job
#
#     @staticmethod
#     def get_schedule(job_id: str, jobstore: str = None) -> Job | None:
#         job = Scheduler._scheduler.get_job(job_id, jobstore)
#         return job
#
#     @staticmethod
#     def start():
#         try:
#             Scheduler._scheduler.start()
#         except SchedulerAlreadyRunningError | RuntimeError as e:
#             logger.error(str(e))
#             raise
#
#     @staticmethod
#     def stop():
#         try:
#             Scheduler._scheduler.shutdown(wait=True)
#         except SchedulerNotRunningError as e:
#             logger.error(str(e))
#             raise
