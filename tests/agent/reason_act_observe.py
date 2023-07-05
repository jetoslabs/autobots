import pytest
import pytest_asyncio

from autobots.agent.reason_act_observe import ReasonActObserve
from autobots.core.settings import get_settings


@pytest_asyncio.fixture
async def set_settings():
    settings = get_settings(_env_file='../.env.local')


@pytest.mark.asyncio
async def test_agent_reason_act_observe_happy_path_1(set_settings):
    # user_goal = "What is the difference in celsius in current temperature in San Francisco and New Delhi"
    user_goal = "What is the nearest costco address for California zipcode 94132"
    # user_goal = "According to medicine science what is the best position to do sex for having a baby"
    messages = await ReasonActObserve().do_task(user_goal=user_goal)
    assert "finish[" in messages[-1].content
