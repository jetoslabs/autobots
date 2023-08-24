from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from autobots.action.action_types import ActionType


class ActionDocFind(BaseModel):
    id: Optional[str] = Field(default=None)#, alias='_id')
    name: Optional[str] = None
    version: Optional[float] = None
    description: Optional[str] = None
    type: Optional[ActionType] = None
    input: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    user_id: Optional[str] = None


class ActionDocCreate(BaseModel):
    name: str
    version: float = 0
    description: str = ""
    type: ActionType
    input: Dict[str, Any]
    created_at: datetime = datetime.now()
    user_id: str


class ActionDoc(ActionDocCreate):
    __collection__ = "Actions"

    id: str = Field(..., alias='_id')
