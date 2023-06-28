from typing import List

import pytest
import pytest_asyncio
from pydantic import HttpUrl

from autobots.action.read_urls import ReadUrlsData, ReadUrls
from autobots.core.settings import get_settings


# Run command `python -m pytest -s` from `autobots/tests` folder
@pytest_asyncio.fixture
async def set_settings():
    settings = get_settings(_env_file='../.env.local')


@pytest.mark.asyncio
async def test_read_urls_happy_path(set_settings):
    read_urls_req: List[HttpUrl] = ["https://meetkiwi.co", "https://google.com"]
    read_urls_data = ReadUrlsData(name="test_read_urls", read_urls_req=read_urls_req)
    await ReadUrls().run(read_urls_data)

    assert "kiwi" in read_urls_data.context[read_urls_req[0]]
    assert "Gmail" in read_urls_data.context[read_urls_req[1]]
