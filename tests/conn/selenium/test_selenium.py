import pytest
from pydantic import HttpUrl

from autobots.conn.selenium.selenium import get_selenium


# TODO: Make Selenium work, currently unable to install chromedriver in image
# @pytest.mark.skip(reason="Selenium driver not working")
@pytest.mark.asyncio
async def test_read_url_text_happy_path(set_test_settings):
    url_text = await get_selenium().read_url_text(HttpUrl("https://google.com"))
    assert "Gmail" in url_text


# TODO: Make Selenium work, currently unable to install chromedriver in image
# @pytest.mark.skip(reason="Selenium driver not working")
@pytest.mark.asyncio
async def test_read_url_happy_path(set_test_settings):
    html = await get_selenium().read_url(HttpUrl("https://google.com"))
    assert "Google" in html
