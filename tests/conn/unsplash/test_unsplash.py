import pytest
import pytest_asyncio

from autobots.conn.unsplash.unsplash import get_unsplash
from autobots.core.settings import get_settings


# Run command `python -m pytest -s` from `autobots/tests` folder
@pytest_asyncio.fixture
async def set_settings():
    settings = get_settings(_env_file='.env.local')


@pytest.mark.asyncio
async def test_random_photo_happy_path(set_settings):
    img_list = await get_unsplash().get_random_photo()
    assert len(img_list) > 0
    assert "https" in img_list[0].urls.thumb


@pytest.mark.asyncio
async def test_search_photos_happy_path(set_settings):
    img_list = await get_unsplash().search_photo("athlete running")
    assert len(img_list.results) > 0
    assert "https" in img_list.results[0].urls.thumb
