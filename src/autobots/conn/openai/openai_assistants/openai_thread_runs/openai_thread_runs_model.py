from typing import Literal, Iterable, Dict

from openai.types.beta import AssistantToolParam, AssistantResponseFormatOptionParam, AssistantToolChoiceOptionParam, \
    thread_create_and_run_params
from openai.types.beta.threads import run_create_params
from openai.types.beta.threads.run_submit_tool_outputs_params import ToolOutput
from pydantic import BaseModel

from src.autobots.conn.openai.openai_models import OPENAI_MODELS


class ThreadRunCreate(BaseModel):
    thread_id: str
    assistant_id: str
    model: OPENAI_MODELS | None = None
    additional_instructions: str | None = None
    additional_messages: Iterable[run_create_params.AdditionalMessage] | None = None
    instructions: str | None = None
    max_completion_tokens: int | None = None
    max_prompt_tokens: int | None = None
    metadata: Dict[str, str] | None = None
    response_format: AssistantResponseFormatOptionParam | None = None
    stream: Literal[False] | Literal[True] | None = None
    temperature: float | None = None
    tool_choice: AssistantToolChoiceOptionParam | None = None
    tools: Iterable[AssistantToolParam] | None = None
    top_p: float | None = None
    truncation_strategy: run_create_params.TruncationStrategy | None = None


class ThreadRunCreateAndRun(BaseModel):
    assistant_id: str
    instructions: str | None = None
    max_completion_tokens: int | None = None
    max_prompt_tokens: int | None = None
    metadata: Dict[str, str] | None = None
    model: OPENAI_MODELS | None = None
    response_format: AssistantResponseFormatOptionParam | None = None
    stream: Literal[False] | Literal[True] | None = None
    temperature: float | None = None
    thread: thread_create_and_run_params.Thread | None = None,
    tool_choice: AssistantToolChoiceOptionParam | None = None
    tool_resources: thread_create_and_run_params.ToolResources | None = None
    tools: Iterable[thread_create_and_run_params.Tool] | None = None
    top_p: float | None = None
    truncation_strategy: thread_create_and_run_params.TruncationStrategy | None = None


class ThreadRunRetrieve(BaseModel):
    thread_id: str
    run_id: str


class ThreadRunUpdate(BaseModel):
    thread_id: str
    run_id: str
    metadata: object | None = None


class ThreadRunList(BaseModel):
    thread_id: str
    limit: int | None = None
    order: Literal["asc", "desc"] | None = None
    after: str | None = None
    before: str | None = None


class ThreadRunSubmitToolOutputs(BaseModel):
    thread_id: str
    run_id: str
    tool_outputs: list[ToolOutput]
    stream: bool | None = None


class ThreadRunCancel(BaseModel):
    thread_id: str
    run_id: str


###################
class ThreadRunStepRetrieve(BaseModel):
    step_id: str
    run_id: str
    thread_id: str


class ThreadRunStepList(BaseModel):
    run_id: str
    thread_id: str
    after: str | None = None
    before: str | None = None
    limit: int | None = None
    order: Literal["asc", "desc"] | None = None
