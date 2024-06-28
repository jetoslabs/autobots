from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import Field, BaseModel, ConfigDict
from pydantic_extra_types.pendulum_dt import DateTime

from src.autobots.action.action.common_action_models import TextObj
from src.autobots.data_model.updated_at import UpdatedAt


class EventType(str, Enum):
    action_run = "action_run"
    action_graph_run = "action_graph_run"
    datastore_put = "datastore_put"


class EventResultStatus(str, Enum):
    success = "success"
    processing = "processing"
    error = "error"
    waiting = "waiting"


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


class EventResultDocUpdate(EventResultUpdate, UpdatedAt):
    id: str
    user_id: str
    # updated_at: datetime = datetime.now()


class EventResultCreate(BaseModel):
    type: EventType
    status: EventResultStatus
    error_message: Optional[TextObj] = None
    is_saved: bool = False
    result: Dict[str, Any] = {}


class EventResultDocCreate(EventResultCreate, UpdatedAt):
    user_id: str
    created_at: datetime = datetime.now()
    # updated_at: datetime = datetime.now()


class EventResultLiteDoc(BaseModel):
    id: str = Field(..., alias='_id')
    user_id: str
    type: EventType
    status: EventResultStatus
    error_message: Optional[TextObj] = None
    is_saved: bool = False
    created_at: datetime
    updated_at: DateTime

    model_config = ConfigDict(populate_by_name=True)


class EventResultDoc(EventResultDocCreate):
    __collection__ = "EventResults"

    id: str = Field(..., alias='_id')

    model_config = ConfigDict(populate_by_name=True)
