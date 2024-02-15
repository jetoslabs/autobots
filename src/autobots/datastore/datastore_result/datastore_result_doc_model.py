from typing import List

from pydantic import BaseModel

from src.autobots.datastore.datastore import DatastoreResult
from src.autobots.event_result.event_result_model import (
    EventResultDoc,
    EventType,
    EventResultCreate,
    EventResultUpdate,
)


class DatastoreResults(BaseModel):
    status_for: List[DatastoreResult] = []


class DatastoreResultUpdate(EventResultUpdate):
    """
    Input from User to update Datastore Result
    """

    result: DatastoreResults | None = None


class DatastoreResultCreate(EventResultCreate):
    type: EventType = EventType.datastore_put.value
    result: DatastoreResults = DatastoreResults()


class DatastoreResultDoc(EventResultDoc):
    result: DatastoreResults | None = None
