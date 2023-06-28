import pytest
import pytest_asyncio

from autobots.conn.conn import get_conn
from autobots.conn.stability.stability import Stability
from autobots.conn.stability.stability_data import StabilityReq
from autobots.core.settings import get_settings


# Run command `python -m pytest -s` from `autobots/tests` folder
@pytest_asyncio.fixture
async def set_settings():
    settings = get_settings(_env_file='../.env.local')


@pytest.mark.asyncio
async def test_text_to_image_happy_path(set_settings):
    prompt = "create a clean image with correct face and correct body for Nike shoes advertisement in India fit for top sports magazine "
    get_conn().stability = Stability(engine="stable-diffusion-768-v2-0")

    stability_req = StabilityReq(prompt=prompt, cfg_scale=9)
    await get_conn().stability.text_to_image(stability_req)
    assert True

