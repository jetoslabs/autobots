from datetime import datetime
from typing import Any, Dict, Optional, List

from pydantic_extra_types.pendulum_dt import DateTime
from pydantic import BaseModel, Field, ConfigDict

from src.autobots.action.action_type.action_types import ActionType
from src.autobots.data_model.updated_at import UpdatedAt


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
    updated_at: Optional[datetime] = None


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


class ActionDocUpdate(ActionUpdate, UpdatedAt):
    id: str
    user_id: str


class ActionResult(BaseModel):
    input: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None


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
    results: List[ActionResult] | None = []
    input: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None
    is_published: bool = False


class ActionDocCreate(ActionCreate, UpdatedAt):
    """
    Add in user id to enforce multi-tenancy
    """
    user_id: str
    created_at: datetime = datetime.now()

class ActionLiteDoc(BaseModel):
    id: str = Field(..., alias='_id')
    type: ActionType
    name: str
    version: float = 0
    description: str = ""
    is_published: bool = False
    user_id: str
    created_at: datetime
    updated_at: DateTime

    model_config = ConfigDict(populate_by_name=True)

class ActionDoc(ActionDocCreate):
    __collection__ = "Actions"

    id: str = Field(..., alias='_id')

    model_config = ConfigDict(populate_by_name=True)
