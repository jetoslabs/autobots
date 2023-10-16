import pytest_asyncio


@pytest_asyncio.fixture
def set_test_settings():
    print("Function scope fixture for test: runs for every test")
