import pytest
import pytest_asyncio

from autobots.core.settings import get_settings
from autobots.datastore.data_provider import DataProvider

FILENAME = "resources/datastore/shopifyql"


@pytest_asyncio.fixture
async def set_settings():
    settings = get_settings(_env_file='../.env.local')


@pytest.mark.asyncio
async def test_read_file_line_by_line_happy_path(set_settings):
    count = 0

    lines = DataProvider.read_file_line_by_line(FILENAME)
    async for line in lines:
        count = count + 1

    assert count == 31


@pytest.mark.asyncio
async def test_create_file_chunks_happy_path(set_settings):
    count = 0

    chunks = DataProvider.create_file_chunks(FILENAME, DataProvider.read_file_line_by_line, 52)

    async for chunk in chunks:
        count = count + 1

    assert count == 3





