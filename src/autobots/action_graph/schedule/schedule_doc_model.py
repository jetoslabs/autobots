from pydantic import Field, ConfigDict, BaseModel

from src.autobots.action.action.common_action_models import TextObj
from src.autobots.action_graph.schedule.trigger import Trigger


class ScheduleFind(BaseModel):
    id: str | None = None
    name: str | None = None
    trigger: Trigger | None = None
    action_graph_id: str | None = None
    user_input: TextObj | None = None
    job_id: str | None = None


class ScheduleDocFind(ScheduleFind):
    user_id: str


class ScheduleUpdate(BaseModel):
    name: str | None = None
    trigger: Trigger | None = None
    action_graph_id: str | None = None
    user_input: TextObj | None = None
    # job_id: str | None = None


class ScheduleDocUpdate(ScheduleUpdate):
    user_id: str


class ScheduleCreate(BaseModel):
    name: str
    trigger: Trigger
    action_graph_id: str
    user_input: TextObj


class ScheduleDocCreate(ScheduleCreate):
    job_id: str
    user_id: str


class ScheduleDoc(ScheduleDocCreate):
    __collection__ = "Schedules"

    id: str = Field(..., alias='_id')

    model_config = ConfigDict(populate_by_name=True)
