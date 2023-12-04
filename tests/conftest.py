import pytest_asyncio
from fastapi.testclient import TestClient

from autobots.main import app

@pytest_asyncio.fixture
def test_client() -> TestClient:
    print("Function scope fixture for test: runs for every test")
    client = TestClient(app)
    return client
