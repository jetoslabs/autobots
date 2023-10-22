import pytest

from autobots.agent.one_step import AgentData, OneStepAgent


# TODO: Make Selenium work, currently unable to install chromedriver in image
# @pytest.mark.skip(reason="One step agent stalling, selenium tests should pass")
@pytest.mark.asyncio
async def test_one_step_happy_path_1(set_test_settings):
    agent_data = AgentData(goal="Act as an effective google search advert maker. Create advert for Nike shoes")
    await OneStepAgent().run(agent_data)
    print("test_one_step_happy_path_1: "+agent_data.context[-1].content)
    assert True
