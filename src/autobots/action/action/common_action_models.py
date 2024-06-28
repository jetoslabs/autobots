from typing import List, Optional

from pydantic import BaseModel

# from autobots.conn.openai.image_model import ImageRes


class TextObj(BaseModel):
    text: str = ""



class TextObjs(BaseModel):
    texts: List[TextObj] = []

class MultiObj(BaseModel):
    text: str = ""
    urls: Optional[List[str]] =[]

class MultiObjs(BaseModel):
    texts: List[TextObj] = []
    urls: Optional[List[str]] =[]

# class ImagesResponse(BaseModel):
#     images: List[ImageRes] = []