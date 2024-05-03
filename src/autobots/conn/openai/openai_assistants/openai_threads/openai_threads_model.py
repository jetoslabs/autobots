from typing import List, Optional

from openai.types.beta import thread_create_params, thread_create_and_run_params

from src.autobots.conn.openai.openai_common_models import OpenaiExtraValues


class ThreadCreateAndRun(OpenaiExtraValues):
    assistant_id: str
    instructions: Optional[str] | None = None
    metadata: Optional[object] | None = None
    model: Optional[str] | None = None
    thread: thread_create_and_run_params.Thread | None = None
    tools: Optional[List[thread_create_and_run_params.Tool]] | None = None


class ThreadCreate(OpenaiExtraValues):
    messages: List[thread_create_params.Message] | None = None
    tool_resources: thread_create_params.ToolResources | None = None
    metadata: Optional[object] | None = None


class ThreadRetrieve(OpenaiExtraValues):
    thread_id: str


class ThreadUpdate(OpenaiExtraValues):
    thread_id: str
    tool_resources: thread_create_params.ToolResources | None = None
    metadata: Optional[object] | None = None


class ThreadDelete(OpenaiExtraValues):
    thread_id: str
