from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from autobots.action.action_types import ActionType
from autobots.conn.openai.chat import ChatReq


class ActionFind(BaseModel):
    """
    Input from User to find action
    """
    id: Optional[str] = Field(default=None)  # , alias='_id')
    name: Optional[str] = None
    version: Optional[float] = None
    description: Optional[str] = None
    type: Optional[ActionType] = None
    input: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None


class ActionDocFind(ActionFind):
    """
    Add in user id to enforce multi-tenancy
    """
    user_id: Optional[str] = None


class ActionUpdate(BaseModel):
    name: Optional[str] = None
    version: Optional[float] = None
    description: Optional[str] = None
    input: Optional[Dict[str, Any]] = None


class ActionDocUpdate(ActionUpdate):
    id: str
    user_id: str


class ActionCreate(BaseModel):
    """
    Input from User to create action
    """
    name: str
    version: float = 0
    description: str = ""
    user_manual: str = ""
    type: ActionType
    input: Dict[str, Any]


class ActionDocCreate(ActionCreate):
    """
    Add in user id to enforce multi-tenancy
    """
    user_id: str
    created_at: datetime = datetime.now()


class ActionDoc(ActionDocCreate):
    __collection__ = "Actions"

    id: str = Field(..., alias='_id')
