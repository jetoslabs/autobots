import time

import pytest

from src.autobots.information.updated_at import UpdatedAt


class SimpleObj(UpdatedAt):
    pass


@pytest.mark.asyncio
async def test_updated_at_happy_path(set_test_settings):
    obj1 = SimpleObj()
    time.sleep(5)
    obj2 = SimpleObj()
    assert obj2.updated_at.diff(obj1.updated_at).as_duration().in_seconds() == 5
