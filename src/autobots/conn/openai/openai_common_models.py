from typing import Mapping

from pydantic import BaseModel, ConfigDict


class OpenaiExtraValues(BaseModel):
    extra_headers: Mapping[str, str] | None = None
    extra_query: Mapping[str, object] | None = None
    extra_body: object | None = None
    timeout: float | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
