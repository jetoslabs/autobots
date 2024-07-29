from typing import List, Optional

from pydantic import BaseModel
from openai.types.beta import AssistantTool
from openai.types.beta.assistant import ToolResources
# from autobots.conn.openai.image_model import ImageRes


class TextObj(BaseModel):
    text: str = ""

class AssistantObj(BaseModel):
    text: str = ""
    urls: Optional[List[str]] =[] 
    tools: Optional[List[AssistantTool]] = []
    tool_resources: Optional[ToolResources] = None


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