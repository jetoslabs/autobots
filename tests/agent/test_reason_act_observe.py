import time

import pytest
import pytest_asyncio

from autobots.agent.reason_act_observe import ReasonActObserve
from autobots.core.settings import get_settings


@pytest_asyncio.fixture
async def set_settings():
    settings = get_settings(_env_file='.env.local')
    # settings.OPENAI_ENGINE = "gpt-3.5-turbo-16k-0613"


@pytest.mark.asyncio
async def test_agent_reason_act_observe_happy_path_1(set_settings):
    # user_goal = "What is the difference in celsius for current temperature between San Francisco and New Delhi"
    # user_goal = "What is the address of the nearest costco to California zipcode 94132"
    # user_goal = "What is value of 30th position in fibonacci series"
    user_goal = "What is the difference between iterable.com and adcreative.ai"
    # user_goal = "How will USA economy grow this year"
    # user_goal = "Arsenal Football club the latest signing"
    # user_goal = "What is the latest political news of India"
    # user_goal = "Tell me the latest transfer for Manchester United"
    # user_goal = "Most starred Github repo" Fail
    # user_goal = "Plan a trip to Hawaii, leaving from San Francisco in budget of $5000"
    # user_goal = "Write a quick blog post on git commands"
    messages = await ReasonActObserve().do_task(user_goal=user_goal)
    assert "finish[" in messages[-1].content
