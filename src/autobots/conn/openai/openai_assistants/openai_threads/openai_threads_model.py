from typing import List, Optional

from openai.types.beta import thread_create_params

from src.autobots.conn.openai.openai_common_models import OpenaiExtraValues


class ThreadCreate(OpenaiExtraValues):
    messages: List[thread_create_params.Message] | None = None
    metadata: Optional[object] | None = None


class ThreadRetrieve(OpenaiExtraValues):
    thread_id: str


class ThreadUpdate(OpenaiExtraValues):
    thread_id: str
    metadata: Optional[object] | None = None


class ThreadDelete(OpenaiExtraValues):
    thread_id: str
