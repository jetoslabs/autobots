from typing import List

from fastapi import HTTPException
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.autobots.action_graph.action_graph.user_action_graph import UserActionGraphs
from src.autobots.action_graph.schedule.schedule import Schedule
from src.autobots.action_graph.schedule.schedule_crud import ScheduleCRUD
from src.autobots.action_graph.schedule.schedule_doc_model import ScheduleDoc, ScheduleDocFind, ScheduleFind, \
    ScheduleCreate, ScheduleDocCreate, ScheduleUpdate, ScheduleDocUpdate
from src.autobots.user.user_orm_model import UserORM


class UserSchedule:

    def __init__(self, user: UserORM, db: AsyncIOMotorDatabase):
        self.user = user
        self.user_id = str(user.id)
        self.db = db
        self.schedule_crud = ScheduleCRUD(db)

    async def create_user_schedule(self, schedule_create: ScheduleCreate) -> ScheduleDoc:
        try:
            job = Schedule().create_schedule(
                func=UserActionGraphs.run_scheduled_action_graph,
                kwargs={
                    "action_graph_id": schedule_create.action_graph_id,
                    "user_id": self.user_id,
                    "input": schedule_create.user_input,
                    # "db": self.db
                },
                trigger=schedule_create.trigger,
                name=schedule_create.name,

            )
            schedule_doc_create = ScheduleDocCreate(
                job_id=job.id,
                user_id=self.user_id,
                **schedule_create.model_dump(exclude_none=True)
            )

            schedule_doc = await self.schedule_crud.insert_one(schedule_doc_create)
            return schedule_doc
        except Exception as e:
            logger.error(str(e))
            raise

    async def list_user_schedule(self, schedule_find: ScheduleFind, limit: int = 100, offset: int = 0) -> List[ScheduleDoc]:
        schedule_doc_find = ScheduleDocFind(user_id=self.user_id, **schedule_find.model_dump())
        schedule_docs = await self.schedule_crud.find(schedule_doc_find, limit=limit, offset=offset)
        return schedule_docs

    async def get_user_schedule(self, schedule_id: str) -> ScheduleDoc:
        schedule_doc_find = ScheduleDocFind(user_id=self.user_id, id=schedule_id)
        schedule_docs = await self.schedule_crud.find(schedule_doc_find)
        if len(schedule_docs) != 1:
            raise HTTPException(500, "Error in finding action")
        return schedule_docs[0]

    async def update_user_schedule(self, schedule_id: str, schedule_update: ScheduleUpdate) -> ScheduleDoc:
        try:
            schedule_doc_find = ScheduleDocFind(user_id=self.user_id, id=schedule_id)
            schedule_docs = await self.schedule_crud.find(schedule_doc_find)
            if len(schedule_docs) != 1:
                raise HTTPException(404, "Schedule does not exist")
            schedule_doc = schedule_docs[0]

            existing_job = Schedule().get_schedule(schedule_doc.job_id)
            assert existing_job is not None

            modify_schedule_dict: dict = {}
            if schedule_update.name:
                modify_schedule_dict["name"] = schedule_update.name
            if schedule_update.trigger:
                modify_schedule_dict["trigger"] = schedule_update.trigger
            if schedule_update.action_graph_id or schedule_update.user_input:
                modify_schedule_dict["kwargs"] = existing_job.kwargs
                if schedule_update.action_graph_id:
                    modify_schedule_dict["kwargs"]["action_graph_id"] = schedule_update.action_graph_id
                if schedule_update.user_input:
                    modify_schedule_dict["kwargs"]["user_input"] = schedule_update.user_input

            modified_job = Schedule().modify_schedule(job_id=existing_job.id, **modify_schedule_dict)  # noqa F841

            schedule_doc_update = ScheduleDocUpdate(
                user_id=self.user_id,
                **schedule_update.model_dump(exclude_none=True)
            )

            schedule_doc = await self.schedule_crud.update_one(schedule_doc_update)
            return schedule_doc
        except Exception as e:
            logger.error(str(e))
            raise

    async def delete_user_schedule(self, schedule_id: str) -> int:
        schedule_doc_find = ScheduleDocFind(user_id=self.user_id, id=schedule_id)
        delete_result = await self.schedule_crud.delete_many(schedule_doc_find)
        return delete_result.deleted_count
