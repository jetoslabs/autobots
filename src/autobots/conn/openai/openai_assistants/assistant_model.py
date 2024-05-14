from typing import Literal, Iterable, Dict, Optional

from openai.types import ChatModel
from openai.types.beta import AssistantToolParam, AssistantResponseFormatOptionParam, assistant_create_params

from src.autobots.conn.openai.openai_common_models import OpenaiExtraValues


class AssistantCreate(OpenaiExtraValues):
    model: ChatModel = "gpt-4o"
    name: str | None = None
    description: str | None = None
    instructions: str | None = None
    metadata: Dict[str, str] | None = None
    tools: Iterable[AssistantToolParam] | None = None
    tool_resources: Optional[assistant_create_params.ToolResources] = None
    temperature: float | None = None
    top_p: Optional[float] = None
    response_format: Optional[AssistantResponseFormatOptionParam] = None


class AssistantRetrieve(OpenaiExtraValues):
    assistant_id: str


class AssistantList(OpenaiExtraValues):
    after: str | None = None
    before: str | None = None
    limit: int | None = None
    order: Literal["asc", "desc"] | None = None


class AssistantDelete(AssistantRetrieve):
    pass


class AssistantUpdate(OpenaiExtraValues):
    assistant_id: str
    model: ChatModel | None = None
    name: str | None = None
    description: str | None = None
    instructions: str | None = None
    tools: Iterable[AssistantToolParam] | None = None
    tool_resources: Optional[assistant_create_params.ToolResources] = None
    metadata: Dict[str, str] | None = None
    temperature: float | None = None
    top_p: Optional[float] = None
    response_format: Optional[AssistantResponseFormatOptionParam] = None


# class AssistantFileInput(OpenaiExtraValues):
#     assistant_id: str
#     file_id: str
#
#
# class AssistantFileListInput(OpenaiExtraValues):
#     assistant_id: str
#     after: str | None = None,
#     before: str | None = None,
#     limit: int | None = None,
#     order: Literal["asc", "desc"] | None = None
#

