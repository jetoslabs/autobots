from typing import List, Any

from fastapi import APIRouter

from src.autobots.action.action.common_action_models import TextObj
from src.autobots.agent.one_step import OneStepAgent, AgentData
from src.autobots.agent.reason_act_observe import ReasonActObserve
from src.autobots.data_model.context import Context

router = APIRouter()


@router.post("/react")
async def run_react_agent(input: TextObj) -> List[Any]:#List[ChatCompletionSystemMessageParam | ChatCompletionUserMessageParam | ChatCompletionAssistantMessageParam | ChatCompletionToolMessageParam | ChatCompletionFunctionMessageParam]:
    ctx = Context()
    messages = await ReasonActObserve().do_task(ctx, input.text)
    return messages


# TODO: Make Selenium work, currently unable to install chromedriver in image
@router.post("/act")
async def run_act_agent(agent_data: AgentData) -> AgentData:
    ctx = Context()
    await OneStepAgent().run(ctx, agent_data, loops_allowed=5)
    return agent_data
