from typing import List, Optional
from pydantic import BaseModel

class PollGraphDoc(BaseModel):
    id: str
    name: str
    description: str
    version: float
    is_published: bool

class PollGraphCreate(BaseModel):
    name: str
    description: str
    version: float
    is_published: bool

class PollGraphFind(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    version: Optional[float] = None
    is_published: Optional[bool] = None

class PollGraphUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[float] = None
    is_published: Optional[bool] = None

class PollGraphDocsFound(BaseModel):
    docs: List[PollGraphDoc]
    total: int

class PollGraphPublishedDocFind(BaseModel):
    # Define any fields necessary for published document finding
    pass