from typing import Literal, Iterable

from openai.types.beta import AssistantToolParam

from src.autobots.conn.openai.openai_common_models import OpenaiExtraValues


class AssistantCreate(OpenaiExtraValues):
    model: Literal[
        "gpt-4-turbo-preview",
        "gpt-4-1106-preview",
        "gpt-4-vision-preview",
        "gpt-4",
        "gpt-4-0314",
        "gpt-4-0613",
        "gpt-4-32k",
        "gpt-4-32k-0314",
        "gpt-4-32k-0613",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-0301",
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
    ] = "gpt-4-turbo-preview"
    description: str | None = None
    file_ids: list[str] | None = None
    instructions: str | None = None
    metadata: object | None = None
    name: str | None = None
    tools: Iterable[AssistantToolParam] | None = None


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
    description: str | None = None
    file_ids: list[str] | None = None
    instructions: str | None = None
    metadata: object | None = None
    model: str | None = None
    name: str | None = None
    tools: Iterable[AssistantToolParam] | None = None


class AssistantFileInput(OpenaiExtraValues):
    assistant_id: str
    file_id: str


class AssistantFileListInput(OpenaiExtraValues):
    assistant_id: str
    after: str | None = None,
    before: str | None = None,
    limit: int | None = None,
    order: Literal["asc", "desc"] | None = None


