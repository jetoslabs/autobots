import pytest

from autobots.datastore.data_provider import DataProvider

FILENAME = "tests/resources/datastore/shopifyql"


@pytest.mark.asyncio
async def test_read_file_line_by_line_happy_path(set_test_settings):
    count = 0

    lines = DataProvider.read_file_line_by_line(FILENAME)
    async for line in lines:
        count = count + 1

    assert count == 31


@pytest.mark.asyncio
async def test_create_file_chunks_happy_path(set_test_settings):
    count = 0

    chunks = DataProvider.create_file_chunks(FILENAME, DataProvider.read_file_line_by_line, 52)

    async for chunk in chunks:
        count = count + 1

    assert count == 3





