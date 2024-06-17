from pydantic import BaseModel, Field
from pydantic_extra_types.pendulum_dt import DateTime

from src.autobots.core.clock.clock import Clock


class UpdatedAt(BaseModel):
    # here DateTime is from package pydantic_extra_types, this is compatible with Pydantic
    updated_at: DateTime = Field(default_factory=lambda: Clock.get_date_time())



