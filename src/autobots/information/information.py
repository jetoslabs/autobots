from typing import Any

from pydantic import BaseModel


class Information(BaseModel):
    data: Any | None = None
    meta: Any | None = None
