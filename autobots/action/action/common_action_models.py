from typing import List

from pydantic import BaseModel


class TextObj(BaseModel):
    text: str = ""


class TextObjs(BaseModel):
    texts: List[TextObj]
