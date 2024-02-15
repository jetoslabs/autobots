from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, ConfigDict

from src.autobots.action.action_type.action_types import ActionType


class ActionFind(BaseModel):
    """
    Input from User to find action
    """

    id: Optional[str] = Field(default=None)  # , alias='_id')
    name: Optional[str] = None
    version: Optional[float] = None
    description: Optional[str] = None
    type: Optional[ActionType] = None
    config: Optional[Dict[str, Any]] = None
    is_published: Optional[bool] = None
    created_at: Optional[datetime] = None


class ActionDocFind(ActionFind):
    """
    Add in user id to enforce multi-tenancy
    """

    user_id: str


class ActionUpdate(BaseModel):
    name: Optional[str] = None
    version: Optional[float] = None
    description: Optional[str] = None
    user_manual: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_published: Optional[bool] = None


class ActionDocUpdate(ActionUpdate):
    id: str
    user_id: str


class ActionCreate(BaseModel):
    """
    base class to be utilized by concrete action types to create action
    """

    name: str
    version: float = 0
    description: str = ""
    user_manual: str = ""
    type: ActionType
    config: Dict[str, Any] = {}
    input: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None
    is_published: bool = False


class ActionDocCreate(ActionCreate):
    """
    Add in user id to enforce multi-tenancy
    """

    user_id: str
    created_at: datetime = datetime.now()


class ActionDoc(ActionDocCreate):
    __collection__ = "Actions"

    id: str = Field(..., alias="_id")

    model_config = ConfigDict(populate_by_name=True)
