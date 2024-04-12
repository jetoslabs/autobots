from asyncio import get_event_loop

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from src.autobots.action_graph.schedule.schedule import Schedule
from src.autobots.main import app


## TODO: Replacing the event_loop fixture with a custom implementation is deprecated and will lead to errors in the future.
@pytest.fixture(scope="session")
def event_loop():
    loop = get_event_loop()
    yield loop

# pytestmark = pytest.mark.asyncio(scope="session")  # If in root conftest.py then Session scope


@pytest_asyncio.fixture
def set_test_settings():
    print("Function scope fixture for test: runs for every test")


@pytest_asyncio.fixture
def test_client() -> TestClient:
    print("Function scope fixture for test: test_client")
    client = TestClient(app)
    return client


@pytest_asyncio.fixture(scope="session")
def apscheduler_setup():
    # print("this is setup")
    yield
    Schedule.stop_scheduler()
    print("apscheduler teardown")
