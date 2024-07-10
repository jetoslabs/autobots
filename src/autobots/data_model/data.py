from typing import Any

from pydantic import BaseModel


class MetaData(BaseModel):
    meta: Any | None = None


class Data(MetaData):
    data: Any | None = None
