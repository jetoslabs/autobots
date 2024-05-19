
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.autobots.action.action_result.action_result_doc_model import ActionResultDoc, \
    ActionResultUpdate, ActionResultCreate, ActionResultLiteDoc, ActionResultDocsFound
from src.autobots.event_result.event_result_crud import EventResultCRUD
from src.autobots.event_result.event_result_model import EventResultDocCreate, EventResultFind, EventResultDocFind, \
    EventResultDocUpdate, EventType
from src.autobots.user.user_orm_model import UserORM


class UserActionResult:

    def __init__(self, user: UserORM, db: AsyncIOMotorDatabase):
        self.user = user
        self.user_id = str(user.id)
        self.event_result_crud = EventResultCRUD(db)

    async def create_action_result(self, action_result: ActionResultCreate) -> ActionResultDoc | None:
        try:
            event_result_doc_create = EventResultDocCreate(user_id=self.user_id, **action_result.model_dump())
            event_result_doc = await self.event_result_crud.insert_one(event_result_doc_create)
            action_result_doc = ActionResultDoc.model_validate(event_result_doc.model_dump())
            return action_result_doc
        except Exception as e:
            logger.error(str(e))
            raise e

    async def list_action_result(
            self, action_result_find: EventResultFind,
            limit: int = 100, offset: int = 0
    ) -> ActionResultDocsFound:
        action_result_find.type = EventType.action_run
        event_result_doc_find = EventResultDocFind(user_id=self.user_id,
                                                   **action_result_find.model_dump(exclude_none=True))
        event_result_docs_page = await self.event_result_crud.find_page(event_result_doc_find, limit, offset)
        action_result_docs = []
        for event_result_doc in event_result_docs_page.docs:
            action_result_doc = ActionResultLiteDoc.model_validate(event_result_doc.model_dump())
            action_result_docs.append(action_result_doc)
        return ActionResultDocsFound(
            docs=action_result_docs,
            total_count=event_result_docs_page.total_count,
            limit=event_result_docs_page.limit,
            offset=event_result_docs_page.offset
        )

    async def get_action_result(
            self, action_result_id: str
    ) -> ActionResultDoc | None:
        try:
            event_result_doc_find = EventResultDocFind(id=action_result_id, user_id=self.user_id)
            event_result_doc = await self.event_result_crud.find_one(event_result_doc_find)
            if event_result_doc is None:
                return None
            action_result_doc = ActionResultDoc.model_validate(event_result_doc.model_dump())
            return action_result_doc
        except Exception as e:
            logger.error(str(e))
        return None

    async def update_action_result(
            self, action_result_id: str, action_update: ActionResultUpdate
    ) -> ActionResultDoc:
        try:
            event_result_doc_update = EventResultDocUpdate(id=action_result_id, user_id=self.user_id,
                                                           **action_update.model_dump())
            event_result_doc = await self.event_result_crud.update_one(event_result_doc_update)
            action_result_doc = ActionResultDoc.model_validate(event_result_doc.model_dump())
            return action_result_doc
        except Exception as e:
            logger.error(str(e))
            raise e

    async def delete_action_result(
            self, id: str
    ) -> int:
        event_result_doc_find = EventResultDocFind(id=id, user_id=self.user_id)
        delete_result = await self.event_result_crud.delete_many(event_result_doc_find)
        return delete_result.deleted_count
