from typing import Mapping

from pydantic import BaseModel


class OpenaiExtraValues(BaseModel):
    extra_headers: Mapping[str, str] | None = None
    extra_query: Mapping[str, object] | None = None
    extra_body: object | None = None
    timeout: float | None = None