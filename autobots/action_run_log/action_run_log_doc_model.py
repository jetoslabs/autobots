from datetime import datetime
from typing import Optional

from pydantic import Field, BaseModel

from autobots.action.action_doc_model import ActionDoc
from autobots.action.action_type.action_types import ActionType


class ActionRunLogFind(BaseModel):
    """
    Input from User to find action
    """
    id: Optional[str]
    action_id: Optional[str] = Field(default=None)  # , alias='_id')
    action_name: Optional[str] = None
    action_version: Optional[float] = None
    action_description: Optional[str] = None
    action_type: Optional[ActionType] = None


class ActionRunLogDocFind(ActionRunLogFind):
    """
    Add in user id to enforce multi-tenancy
    """
    action_user_id: Optional[str] = None


class ActionRunLog(BaseModel):
    action: ActionDoc


class ActionRunLogDoc(ActionRunLog):
    __collection__ = "ActionRunLogs"

    id: str = Field(..., alias='_id')
    created_at: datetime = datetime.now()


    class Config:
        populate_by_name = True
