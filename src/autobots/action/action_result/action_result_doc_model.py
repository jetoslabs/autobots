from typing import Optional

from src.autobots.action.action.action_doc_model import ActionDoc
from src.autobots.event_result.event_result_model import EventResultCreate, EventResultUpdate, EventResultDoc, EventType


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
