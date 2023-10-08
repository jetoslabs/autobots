import pytest
import pytest_asyncio
from pydantic import HttpUrl

from autobots.conn.selenium.selenium import get_selenium
from autobots.core.settings import get_settings


# Run command `python -m pytest -s` from `autobots/tests` folder
@pytest_asyncio.fixture
async def set_settings():
    settings = get_settings(_env_file='.env.local')


# @pytest.mark.skip(reason="Selenium driver not working")
@pytest.mark.asyncio
async def test_read_url_text_happy_path(set_settings):
    url_text = await get_selenium().read_url_text(HttpUrl("https://google.com"))
    assert "Gmail" in url_text


@pytest.mark.asyncio
async def test_read_url_happy_path(set_settings):
    html = await get_selenium().read_url(HttpUrl("https://google.com"))
    assert "Google" in html
