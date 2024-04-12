from typing import List, Dict, Any

from fastapi import HTTPException, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.autobots.action.action.action_crud import ActionCRUD
from src.autobots.action.action.action_doc_model import ActionDoc, ActionUpdate
from src.autobots.action.action.user_actions import UserActions
from src.autobots.action.action_market.action_market_crud import ActionMarketCRUD
from src.autobots.action.action_market.action_market_model import ActionMarketFind, ActionMarketDocFind
from src.autobots.action.action_result.action_result_doc_model import ActionResultDoc
from src.autobots.action.action_result.user_action_result import UserActionResult
from src.autobots.action.action_type.action_factory import ActionFactory
from src.autobots.api.webhook import Webhook
from src.autobots.user.user_orm_model import UserORM


class UserActionsMarket:

    def __init__(self, user: UserORM, db: AsyncIOMotorDatabase):
        self.user = user
        self.user_id = str(user.id)
        self.action_crud = ActionCRUD(db)
        self.action_market_crud = ActionMarketCRUD(db)
        self._user_actions = UserActions(user, db)

    async def create_market_action(self, id: str) -> ActionDoc:
        action_doc = await self._user_actions.get_action(id)
        # Check if action being published is owned by user
        if not action_doc or not str(self.user.id) == action_doc.user_id:
            raise HTTPException(403, "User dont own this action")
        # publish action
        action_update = ActionUpdate(is_published=True)
        updated_action = await self._user_actions.update_action(id, action_update)
        return updated_action

    async def list_market_actions(
            self, action_market_find: ActionMarketFind,
            limit: int = 100, offset: int = 0
    ) -> List[ActionDoc]:
        # Market actions will have `is_published = True`
        # action_find.is_published = True
        action_doc_find = ActionMarketDocFind(**action_market_find.model_dump())
        action_docs = await self.action_market_crud.find(action_doc_find, limit, offset)
        published_actions = []
        for action_doc in action_docs:
            action_doc.config = {}
            published_actions.append(action_doc)
        return published_actions

    async def get_market_action(self, id: str) -> ActionDoc | None:
        action_find = ActionMarketFind(id=id)
        action_docs = await self.list_market_actions(action_find, 1, 0)
        if len(action_docs) != 1:
            return None
        action_doc = action_docs[0]
        return action_doc

    async def delete_market_action(self, id: str):
        """
        Unpublish market action
        """
        action_doc = await self._user_actions.get_action(id)
        # Check if action being published is owned by user
        if not action_doc or not self.user_id == action_doc.user_id:
            raise HTTPException(403, "User dont own this action")
        # unpublish action
        action_update = ActionUpdate(is_published=False)
        updated_action = await self._user_actions.update_action(id, action_update)
        return updated_action

    async def run_market_action(self, action_id: str, input: Dict[str, Any]) -> ActionDoc:
        # Only get action if it is published in market
        # Market actions will have `is_published = True`
        action_find = ActionMarketFind(id=action_id)
        action_market_doc_find = ActionMarketDocFind(**action_find.model_dump())
        action_docs = await self.action_market_crud.find(action_market_doc_find, 1, 0)
        action_doc = action_docs[0]
        resp = await self._user_actions.run_action_doc(action_doc, input)
        return resp

    async def run_market_action_async(
            self, action_id: str, input: Dict[str, Any], user_action_result: UserActionResult,
            background_tasks: BackgroundTasks = None, webhook: Webhook | None = None
    ) -> ActionResultDoc:
        # Only get action if it is published in market
        # Market actions will have `is_published = True`
        action_find = ActionMarketFind(id=action_id)
        action_market_doc_find = ActionMarketDocFind(**action_find.model_dump())
        action_docs = await self.action_market_crud.find(action_market_doc_find, 1, 0)
        action_doc = action_docs[0]

        action_result_doc = await ActionFactory().run_action_in_background(action_doc, input, user_action_result,
                                                                           background_tasks, webhook)
        return action_result_doc
