import pytest_asyncio
from fastapi.testclient import TestClient

from src.autobots.action_graph.schedule.schedule import Schedule
from src.autobots.main import app


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
