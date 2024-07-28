from typing import List, Any

from fastapi import APIRouter
from starlette.requests import Request

from src.autobots.action.action.common_action_models import TextObj
from src.autobots.agent.one_step import OneStepAgent, AgentData
from src.autobots.agent.reason_act_observe import ReasonActObserve

router = APIRouter()


@router.post("/react")
async def run_react_agent(input: TextObj, request: Request) -> List[Any]:#List[ChatCompletionSystemMessageParam | ChatCompletionUserMessageParam | ChatCompletionAssistantMessageParam | ChatCompletionToolMessageParam | ChatCompletionFunctionMessageParam]:
    ctx = request.state.context
    messages = await ReasonActObserve().do_task(ctx, input.text)
    return messages


# TODO: Make Selenium work, currently unable to install chromedriver in image
@router.post("/act")
async def run_act_agent(agent_data: AgentData, request: Request) -> AgentData:
    ctx = request.state.context
    await OneStepAgent().run(ctx, agent_data, loops_allowed=5)
    return agent_data
