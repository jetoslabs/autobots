from typing import Optional

from autobots.action_graph.action_graph.action_graph_doc_model import ActionGraphDoc
from autobots.event_result.event_result_model import EventResultUpdate, EventResultCreate, EventType, EventResultDoc


class ActionGraphResultUpdate(EventResultUpdate):
    """
    Input from User to update Action Result
    """
    result: Optional[ActionGraphDoc] = None


class ActionGraphResultCreate(EventResultCreate):
    type: EventType = EventType.action_graph_run
    result: ActionGraphDoc


class ActionGraphResultDoc(EventResultDoc):
    result: ActionGraphDoc
