import pytest_asyncio
from fastapi.testclient import TestClient

from src.autobots.main import app


@pytest_asyncio.fixture
def set_test_settings():
    print("Function scope fixture for test: runs for every test")


@pytest_asyncio.fixture
def test_client() -> TestClient:
    print("Function scope fixture for test: test_client")
    client = TestClient(app)
    return client
