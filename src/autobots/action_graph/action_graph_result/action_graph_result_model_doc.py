from typing import Optional, List


from src.autobots.action_graph.action_graph.action_graph_doc_model import ActionGraphDoc, ActionGraphLiteDoc
from src.autobots.core.database.mongo_base_crud import DocFindPage
from src.autobots.event_result.event_result_model import EventResultUpdate, EventResultCreate, EventType, \
    EventResultDoc, EventResultLiteDoc


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


class ActionGraphResultLiteDoc(EventResultLiteDoc):
    result: Optional[ActionGraphLiteDoc] = None


class ActionGraphResultDocsFound(DocFindPage):
    docs: List[ActionGraphResultLiteDoc]
