import pytest

from autobots.agent.reason_act_observe import ReasonActObserve


@pytest.mark.skip(reason="agent stalling")
@pytest.mark.timeout(180)
@pytest.mark.asyncio
async def test_agent_reason_act_observe_happy_path_1(set_test_settings):
    # user_goal = "What is the difference in celsius for current temperature between San Francisco and New Delhi"
    # user_goal = "What is the address of the nearest costco to California zipcode 94132"
    # user_goal = "What is value of 30th position in fibonacci series"
    user_goal = "What is the difference between iterable.com and mailchimp.com"
    # user_goal = "How will USA economy grow this year"
    # user_goal = "Arsenal Football club the latest signing"
    # user_goal = "What is the latest political news of India"
    # user_goal = "Tell me the latest transfer for Manchester United"
    # user_goal = "Most starred Github repo" Fail
    # user_goal = "Plan a trip to Hawaii, leaving from San Francisco in budget of $5000"
    # user_goal = "Write a quick blog post on git commands"
    messages = await ReasonActObserve().do_task(user_goal=user_goal)
    print("test_agent_reason_act_observe_happy_path_1: " + messages[-1]["content"])
    assert "finish[" in messages[-1]["content"]
