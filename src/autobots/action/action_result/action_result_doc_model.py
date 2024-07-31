from typing import Optional, List

from pydantic import BaseModel

from src.autobots.action.action.action_doc_model import ActionDoc, ActionLiteDoc
from src.autobots.event_result.event_result_model import EventResultCreate, EventResultUpdate, EventResultDoc, \
    EventType, EventResultLiteDoc


class ActionResultUpdate(EventResultUpdate):
    """
    Input from User to update Action Result
    """
    result: Optional[ActionDoc] = None


class ActionResultCreate(EventResultCreate):
    type: EventType = EventType.action_run.value
    result: ActionDoc


class ActionResultDoc(EventResultDoc):
    result: ActionDoc


class ActionResultLiteDoc(EventResultLiteDoc):
    result: Optional[ActionLiteDoc] = None


class ActionResultDocsFound(BaseModel):
    docs: List[ActionResultLiteDoc]
    total_count: int
    limit: int
    offset: int
