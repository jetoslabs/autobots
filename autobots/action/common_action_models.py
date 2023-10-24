from pydantic import BaseModel


class TextObj(BaseModel):
    text: str = ""
