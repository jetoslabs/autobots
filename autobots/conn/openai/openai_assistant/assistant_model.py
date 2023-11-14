from typing import Optional, List, Literal

from openai.types.beta import assistant_create_params
from pydantic import BaseModel


class AssistantCreate(BaseModel):
    model: Literal[
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
    ] = "gpt-4"
    description: Optional[str] = ""
    file_ids: List[str] = []
    instructions: Optional[str] = None
    metadata: Optional[object] = {}
    name: Optional[str] = None
    tools: List[assistant_create_params.Tool] | None = None,
    # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
    # The extra values given here take precedence over values defined on the client or passed to this method.
    # extra_headers: Headers | None = None,
    # extra_query: Query | None = None,
    # extra_body: Body | None = None,
    # timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,