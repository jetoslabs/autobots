from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import Field, BaseModel

from autobots.action.action.action_doc_model import ActionDoc
from autobots.action.action_type.action_types import ActionType


class ActionResultStatus(str, Enum):
    success = "success"
    processing = "processing"
    error = "error"


class ActionResultFind(BaseModel):
    """
    Input from User to find action
    """
    id: Optional[str]
    is_saved: Optional[bool] = None
    action_id: Optional[str] = Field(default=None)  # , alias='_id')
    action_name: Optional[str] = None
    action_version: Optional[float] = None
    action_description: Optional[str] = None
    action_type: Optional[ActionType] = None


class ActionResultDocFind(ActionResultFind):
    """
    Add in user id to enforce multi-tenancy
    """
    user_id: str


class ActionResultUpdate(BaseModel):
    """
    Input from User to update Action Result
    """
    status: Optional[ActionResultStatus] = None
    is_saved: Optional[bool] = None
    action: Optional[ActionDoc] = None


class ActionResultDocUpdate(ActionResultUpdate):
    id: str
    user_id: str


class ActionResultCreate(BaseModel):
    status: ActionResultStatus
    action: ActionDoc
    is_saved: bool = False


class ActionResultDocCreate(ActionResultCreate):
    user_id: str
    created_at: datetime = datetime.now()


class ActionResultDoc(ActionResultDocCreate):
    __collection__ = "ActionResults"

    id: str = Field(..., alias='_id')

    class Config:
        populate_by_name = True
