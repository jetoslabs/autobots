from typing import List

from pydantic import BaseModel

# from autobots.conn.openai.image_model import ImageRes


class TextObj(BaseModel):
    text: str = ""


class TextObjs(BaseModel):
    texts: List[TextObj] = []


# class ImagesResponse(BaseModel):
#     images: List[ImageRes] = []