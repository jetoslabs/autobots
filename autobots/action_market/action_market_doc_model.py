from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from autobots.action.action_doc_model import ActionDoc
from autobots.action.action_type.action_types import ActionType


class ActionMarketFind(BaseModel):
    """
    Input from User to find action
    """
    id: Optional[str] = Field(default=None)  # , alias='_id')
    action_user_id: Optional[str] = None
    action_name: Optional[str] = None
    action_version: Optional[float] = None
    action_type: Optional[ActionType] = None


class ActionMarketDocFind(ActionMarketFind):
    """
    Add in user id to enforce multi-tenancy
    """
    user_id: Optional[str] = None


class ActionMarketUpdate(BaseModel):
    action: ActionDoc


class ActionMarketDocUpdate(ActionMarketUpdate):
    id: str
    user_id: str


class ActionMarketCreate(BaseModel):
    """
    base class to be utilized by concrete action types to create action
    """
    action: ActionDoc


class ActionMarketDocCreate(ActionMarketCreate):
    """
    Add in user id to enforce multi-tenancy
    """
    user_id: str
    created_at: datetime = datetime.now()


class ActionMarketDoc(ActionMarketDocCreate):
    __collection__ = "ActionMarket"

    id: str = Field(..., alias='_id')

    class Config:
        populate_by_name = True
