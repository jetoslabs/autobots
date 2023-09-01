from datetime import datetime
from typing import Dict, List, Optional

from pydantic import Field, BaseModel


class ActionGraphFind(BaseModel):
    """
    Input from User to find action_graph
    """
    id: Optional[str] = Field(default=None)  # , alias='_id')
    name: Optional[str] = None
    version: Optional[float] = None
    description: Optional[str] = None
    graph: Optional[Dict[str, List[str]]] = None
    created_at: Optional[datetime] = None


class ActionGraphDocFind(ActionGraphFind):
    """
    Add in user id to enforce multi-tenancy
    """
    user_id: Optional[str] = None


class ActionGraphUpdate(BaseModel):
    name: Optional[str] = None
    version: Optional[float] = None
    description: Optional[str] = None
    graph: Optional[Dict[str, List[str]]] = None


class ActionGraphDocUpdate(ActionGraphUpdate):
    id: str
    user_id: str


class ActionGraphCreate(BaseModel):
    """
    Input from User to create action_graph
    """
    name: str
    version: float = 0
    description: str = ""
    graph: Dict[str, List[str]]


class ActionGraphDocCreate(ActionGraphCreate):
    """
    Add in user id to enforce multi-tenancy
    """
    user_id: str
    created_at: datetime = datetime.now()


class ActionGraphDoc(ActionGraphDocCreate):
    __collection__ = "ActionGraphs"

    id: str = Field(..., alias='_id')

