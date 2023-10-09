from typing import List

from fastapi import APIRouter

from autobots.agent.one_step import OneStepAgent, AgentData
from autobots.agent.reason_act_observe import ReasonActObserve
from autobots.conn.openai.chat import Message
from autobots.prompts.user_prompts import TextObj

router = APIRouter()


@router.post("/react")
async def run_react_agent(input: TextObj) -> List[Message]:
    messages = await ReasonActObserve().do_task(input.text)
    return messages


@router.post("/act")
async def run_act_agent(agent_data: AgentData) -> AgentData:
    await OneStepAgent().run(agent_data, loops_allowed=7)
    return agent_data
