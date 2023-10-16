import pytest_asyncio

from autobots.core.settings import SettingsProvider


@pytest_asyncio.fixture
def set_test_settings():
    print("Settings for tests")
    SettingsProvider.set(".env.test")
    settings = SettingsProvider.sget()
    yield settings
