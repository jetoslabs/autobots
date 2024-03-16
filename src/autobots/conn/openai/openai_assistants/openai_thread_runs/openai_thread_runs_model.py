from typing import Literal, Iterable

from openai.types.beta import AssistantToolParam
from openai.types.beta.threads.run_submit_tool_outputs_params import ToolOutput

from src.autobots.conn.openai.openai_common_models import OpenaiExtraValues


class ThreadRunCreate(OpenaiExtraValues):
    thread_id: str
    assistant_id: str
    instructions: str | None = None
    metadata: object | None = None
    model: str | None = None
    tools: Iterable[AssistantToolParam] | None = None


class ThreadRunRetrieve(OpenaiExtraValues):
    run_id: str
    thread_id: str


class ThreadRunUpdate(OpenaiExtraValues):
    run_id: str
    thread_id: str
    metadata: object | None = None


class ThreadRunList(OpenaiExtraValues):
    thread_id: str
    after: str | None = None
    before: str | None = None
    limit: int | None = None
    order: Literal["asc", "desc"] | None = None


class ThreadRunSubmitToolOutputs(OpenaiExtraValues):
    run_id: str
    thread_id: str
    tool_outputs: list[ToolOutput]


class ThreadRunCancel(OpenaiExtraValues):
    run_id: str
    thread_id: str

class ThreadRunStepRetrieve(OpenaiExtraValues):
    step_id: str
    run_id: str
    thread_id: str

class ThreadRunStepList(OpenaiExtraValues):
    run_id: str
    thread_id: str
    after: str | None = None
    before: str | None = None
    limit: int | None = None
    order: Literal["asc", "desc"] | None = None



