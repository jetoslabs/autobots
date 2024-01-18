from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import Field, BaseModel

from autobots.action.action.common_action_models import TextObj


class EventType(str, Enum):
    action_run = "action_run"
    action_graph_run = "action_graph_run"
    datastore_put = "datastore_put"


class EventResultStatus(str, Enum):
    success = "success"
    processing = "processing"
    error = "error"


class EventResultFind(BaseModel):
    id: Optional[str] = None
    type: Optional[EventType] = None
    status: Optional[EventResultStatus] = None
    is_saved: Optional[bool] = None
    # result: Optional[Dict[str, Any]] = None


class EventResultDocFind(EventResultFind):
    user_id: str


class EventResultUpdate(BaseModel):
    type: Optional[EventType] = None
    status: Optional[EventResultStatus] = None
    error_message: Optional[TextObj] = None
    is_saved: Optional[bool] = None
    result: Optional[Dict[str, Any]] = None


class EventResultDocUpdate(EventResultUpdate):
    id: str
    user_id: str
    updated_at: datetime = datetime.now()


class EventResultCreate(BaseModel):
    type: EventType
    status: EventResultStatus
    error_message: Optional[TextObj] = None
    is_saved: bool = False
    result: Dict[str, Any] = {}


class EventResultDocCreate(EventResultCreate):
    user_id: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class EventResultDoc(EventResultDocCreate):
    __collection__ = "EventResults"

    id: str = Field(..., alias='_id')

    class Config:
        populate_by_name = True
