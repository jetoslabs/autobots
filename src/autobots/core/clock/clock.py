from functools import lru_cache

import pendulum.tz
from pendulum import Timezone, FixedTimezone
from pydantic_extra_types.pendulum_dt import DateTime

from src.autobots import SettingsProvider


class Clock:

    @staticmethod
    @lru_cache
    def get_time_zone(timezone: str = SettingsProvider.sget().TIMEZONE) -> Timezone | FixedTimezone:
        return pendulum.timezone(timezone)

    @staticmethod
    def get_date_time() -> DateTime:
        return pendulum.now(Clock.get_time_zone())
