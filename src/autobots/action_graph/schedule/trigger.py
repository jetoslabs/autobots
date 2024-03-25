import datetime
from typing import Union, Literal

from pydantic import Field, BaseModel


class IntervalTrigger(BaseModel):
    trigger: Literal["interval"] = "interval"
    seconds: int = Field(86400, ge=300)


class CronTrigger(BaseModel):
    """https://crontab.cronhub.io/"""
    trigger: Literal["cron"] = "cron"
    year: str | None = Field(None, ge=1970)
    month: str | None = Field(None)
    day: str | None = Field(None)
    week: str | None = Field(None)
    day_of_week: str | None = Field(None)
    hour: str | None = Field(None)
    minute: str | None = Field(None)
    second: str | None = Field(None)
    start_date: datetime.datetime | None = None
    end_date: datetime.datetime | None = None
    timezone: str | None = None
    jitter: str | None = None


Trigger = Union[IntervalTrigger, CronTrigger]
