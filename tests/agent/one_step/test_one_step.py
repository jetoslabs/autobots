import pytest
import pytest_asyncio

from autobots.agent.one_step import AgentData, OneStepAgent
from autobots.core.settings import get_settings


@pytest_asyncio.fixture
async def set_settings():
    settings = get_settings(_env_file='../.env.local')
    settings.OPENAI_ENGINE = "gpt-3.5-turbo-16k-0613"


@pytest.mark.skip(reason="One step agent stalling, selenium tests should pass")
@pytest.mark.asyncio
async def test_one_step_happy_path_1(set_settings):
    agent_data = AgentData(goal="Advert for Nike shoes")
    await OneStepAgent().run(agent_data)
    print(agent_data.model_dump_json())
    assert True
