import pytest

from autobots.conn.conn import get_conn


@pytest.mark.asyncio
async def test_read_url_happy_path():

    url_text = await get_conn().selenium.read_url_text("https://meetkiwi.co")
    assert "Meetkiwi" in url_text

