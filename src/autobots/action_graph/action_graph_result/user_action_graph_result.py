from typing import List

from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.autobots.action_graph.action_graph.action_graph_doc_model import ActionGraphDoc
from src.autobots.action_graph.action_graph_result.action_graph_result_model_doc import ActionGraphResultDoc, \
    ActionGraphResultCreate, ActionGraphResultUpdate, ActionGraphResultDocsFound, ActionGraphResultLiteDoc
from src.autobots.event_result.event_result_crud import EventResultCRUD
from src.autobots.event_result.event_result_model import EventResultDocCreate, EventResultFind, EventResultDocFind, \
    EventResultDocUpdate, EventType
from src.autobots.user.user_orm_model import UserORM


class UserActionGraphResult:

    def __init__(self, user: UserORM, db: AsyncIOMotorDatabase):
        self.user = user
        self.user_id = str(user.id)
        self.event_result_crud = EventResultCRUD(db)

    async def create_action_graph_result(self,
                                         action_graph_result: ActionGraphResultCreate) -> ActionGraphResultDoc | None:
        try:
            event_result_doc_create = EventResultDocCreate(user_id=self.user_id, **action_graph_result.model_dump())
            event_result_doc = await self.event_result_crud.insert_one(event_result_doc_create)
            action_result_doc = ActionGraphResultDoc.model_validate(event_result_doc.model_dump())
            return action_result_doc
        except Exception as e:
            logger.error(str(e))
            raise e

    async def list_page_action_graph_result(
            self, action_graph_result_find: EventResultFind,
            limit: int = 100, offset: int = 0
    ) -> ActionGraphResultDocsFound:
        action_graph_result_find.type = EventType.action_graph_run
        event_result_doc_find = EventResultDocFind(user_id=self.user_id, **action_graph_result_find.model_dump())
        doc_find_page = await self.event_result_crud.find_page(doc_find=event_result_doc_find, limit=limit,
                                                               offset=offset)
        action_graph_result_docs = []
        for event_result_doc in doc_find_page.docs:
            action_graph_result_lite_doc = ActionGraphResultLiteDoc.model_validate(event_result_doc.model_dump())
            action_graph_result_docs.append(action_graph_result_lite_doc)
        return ActionGraphResultDocsFound(
            docs=action_graph_result_docs,
            total_count=doc_find_page.total_count,
            limit=doc_find_page.limit,
            offset=doc_find_page.offset
        )

    async def list_action_graph_result(
            self, action_graph_result_find: EventResultFind,
            limit: int = 100, offset: int = 0
    ) -> List[ActionGraphResultDoc]:
        action_graph_result_find.type = EventType.action_graph_run
        event_result_doc_find = EventResultDocFind(user_id=self.user_id, **action_graph_result_find.model_dump())
        event_result_docs = await self.event_result_crud.find(event_result_doc_find, limit=limit, offset=offset)
        action_graph_result_docs = []
        for event_result_doc in event_result_docs:
            action_graph_result_doc = ActionGraphResultDoc.model_validate(event_result_doc.model_dump())
            action_graph_result_docs.append(action_graph_result_doc)
        return action_graph_result_docs

    async def get_action_graph_result(
            self, action_graph_result_id: str
    ) -> ActionGraphResultDoc | None:
        try:
            event_result_doc_find = EventResultDocFind(id=action_graph_result_id, user_id=self.user_id)
            event_result_doc = await self.event_result_crud.find_one(event_result_doc_find)
            if event_result_doc is None:
                return None
            action_graph_result_doc: ActionGraphResultDoc = ActionGraphResultDoc.model_validate(
                event_result_doc.model_dump())
            await self._remove_ip_from_published_graphs([action_graph_result_doc])
            return action_graph_result_doc
        except Exception as e:
            logger.error(str(e))
        return None

    async def update_action_graph_result(
            self, action_graph_result_id: str, action_graph_update: ActionGraphResultUpdate
    ) -> ActionGraphResultDoc:
        try:
            event_result_doc_update = EventResultDocUpdate(
                id=action_graph_result_id,
                user_id=self.user_id,
                **action_graph_update.model_dump()
            )
            event_result_doc = await self.event_result_crud.update_one(event_result_doc_update)
            action_graph_result_doc = ActionGraphResultDoc.model_validate(event_result_doc.model_dump())
            return action_graph_result_doc
        except Exception as e:
            logger.error(str(e))
            raise e

    async def delete_action_graph_result(
            self, id: str
    ) -> int:
        event_result_doc_find = EventResultDocFind(id=id, user_id=self.user_id)
        delete_result = await self.event_result_crud.delete_many(event_result_doc_find)
        return delete_result.deleted_count

    async def _remove_ip_from_published_graphs(self, action_graph_result_docs: List[ActionGraphResultDoc]) -> None:
        # User will not see Config objects of Nodes in a Published Graph
        for action_graph_result_doc in action_graph_result_docs:
            try:
                action_graph_doc: ActionGraphDoc = action_graph_result_doc.result
                if action_graph_doc.user_id != self.user_id:
                    for node_id in action_graph_doc.output.keys():
                        action_graph_doc.output.get(node_id).config = {}
            except Exception as e:
                logger.exception(str(e))
