import pytest
import pytest_asyncio

from autobots.action.stability_chat import StabilityChatData, StabilityChat
from autobots.conn.stability.stability import Stability
from autobots.conn.stability.stability_data import StabilityReq
from autobots.core.settings import get_settings


# Run command `python -m pytest -s` from `autobots/tests` folder
@pytest_asyncio.fixture
async def set_settings():
    settings = get_settings(_env_file='../.env.local')
    # Making test cheaper by using old engine
    # stability = Stability(engine="stable-diffusion-768-v2-0")


@pytest.mark.asyncio
async def test_stability_chat_happy_path(set_settings):
    prompt = "Create a general design placeholder template without object for instagram advertisement"
    stability_req = StabilityReq(prompt=prompt)
    chat_data = StabilityChatData(name="test_stability_chat", stability_req=stability_req)

    result = await StabilityChat().run(chat_data)

    assert result.image_bytes is not None

