from typing import List
from uuid import UUID

import gotrue
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pymongo.database import Database

from src.autobots import SettingsProvider
from src.autobots.action_graph.schedule.schedule_doc_model import ScheduleCreate, ScheduleDoc, ScheduleFind, \
    ScheduleUpdate
from src.autobots.action_graph.schedule.user_schedule import UserSchedule
from src.autobots.auth.security import get_user_from_access_token
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.user.user_orm_model import UserORM

router = APIRouter(prefix=SettingsProvider.sget().API_SCHEDULES, tags=[SettingsProvider.sget().API_SCHEDULES])


@router.post("/")
async def create_schedule(
        schedule_create: ScheduleCreate,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ScheduleDoc:
    try:
        user_orm = UserORM(id=UUID(user_res.user.id))
        resp = await UserSchedule(user=user_orm, db=db).create_user_schedule(schedule_create)
        return resp
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(500)


@router.get("/")
async def list_schedules(
        id: str = None, name: str = None, action_graph_id: str = None,
        limit: int = 100, offset: int = 0,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> List[ScheduleDoc]:
    user_orm = UserORM(id=UUID(user_res.user.id))
    find = ScheduleFind(id=id, name=name, action_graph_id=action_graph_id)
    action_docs = await UserSchedule(user=user_orm, db=db).list_user_schedule(find, limit, offset)
    return action_docs


@router.get("/{id}")
async def get_schedule(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ScheduleDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    action_doc = await UserSchedule(user=user_orm, db=db).get_user_schedule(id)
    return action_doc


@router.put("/{id}")
async def update_schedule(
        id: str,
        schedule_update: ScheduleUpdate,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ScheduleDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    action_doc = await UserSchedule(user=user_orm, db=db).update_user_schedule(id, schedule_update)
    return action_doc


@router.delete("/{id}")
async def delete_schedule(
        id: str,
        user_res: gotrue.UserResponse = Depends(get_user_from_access_token),
        db: Database = Depends(get_mongo_db)
) -> ScheduleDoc:
    user_orm = UserORM(id=UUID(user_res.user.id))
    user_schedule = UserSchedule(user=user_orm, db=db)
    schedule_doc = await user_schedule.get_user_schedule(id)
    if schedule_doc is None:
        raise HTTPException(400, "Schedule not found")
    deleted_count = await user_schedule.delete_user_schedule(id)
    if deleted_count != 1:
        raise HTTPException(500, "Error in deleting schedule")
    return schedule_doc
