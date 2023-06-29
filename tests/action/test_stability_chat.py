import pytest
import pytest_asyncio

from autobots.action.stability_chat import StabilityChatData, StabilityChat
from autobots.conn.stability.stability_data import StabilityReq
from autobots.core.settings import get_settings


# Run command `python -m pytest -s` from `autobots/tests` folder
@pytest_asyncio.fixture
async def set_settings():
    settings = get_settings(_env_file='../.env.local')


@pytest.mark.asyncio
async def test_stability_chat_happy_path(set_settings):
    prompt = "create a clean image with correct face and correct body for Nike shoes advertisement in India fit for top sports magazine "
    stability_req = StabilityReq(prompt=prompt)
    chat_data = StabilityChatData(name="test_stability_chat", stability_req=stability_req)

    result = await StabilityChat().run(chat_data)

    assert result.image_bytes is not None

