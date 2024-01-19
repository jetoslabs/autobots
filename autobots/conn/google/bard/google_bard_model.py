from typing import Optional

from bardapi import Tool
from pydantic import BaseModel


class GoogleBardAsk(BaseModel):
    text: str
    image: Optional[bytes] = None
    image_name: Optional[str] = None
    tool: Optional[Tool] = None

