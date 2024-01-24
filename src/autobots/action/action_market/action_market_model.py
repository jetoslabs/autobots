from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.autobots.action.action_type.action_types import ActionType


class ActionMarketFind(BaseModel):
    """
    Input from User to find action
    """
    id: Optional[str] = Field(default=None)  # , alias='_id')
    name: Optional[str] = None
    version: Optional[float] = None
    description: Optional[str] = None
    type: Optional[ActionType] = None
    created_at: Optional[datetime] = None


class ActionMarketDocFind(ActionMarketFind):
    """
    Action if published can be fetched, not connected to user_id
    """
    is_published: bool = True
