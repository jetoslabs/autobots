import pytest
import pytest_asyncio

from autobots.conn.conn import get_conn
from autobots.core.settings import get_settings


# Run command `python -m pytest -s` from `autobots/tests` folder
@pytest_asyncio.fixture
async def set_settings():
    settings = get_settings(_env_file='../.env.local')


@pytest.mark.asyncio
async def test_read_url_happy_path(set_settings):

    url_text = await get_conn().selenium.read_url_text("https://meetkiwi.co")
    assert "Meetkiwi" in url_text

