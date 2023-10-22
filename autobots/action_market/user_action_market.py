from typing import List, Any

from fastapi import HTTPException
from pymongo.database import Database

from autobots.action.action_manager import ActionManager
from autobots.action_market.action_market_crud import ActionMarketCRUD
from autobots.action_market.action_market_doc_model import ActionMarketCreate, ActionMarketDoc, ActionMarketDocCreate, \
    ActionMarketFind, ActionMarketDocFind, ActionMarketUpdate, ActionMarketDocUpdate
from autobots.core.log import log
from autobots.prompts.user_prompts import TextObj
from autobots.user.user_orm_model import UserORM


class UserActionMarket:

    def __init__(self, user: UserORM, db: Database):
        self.user = user
        self.user_id = str(user.id)
        self.action_market_crud = ActionMarketCRUD(db)

    async def create_market_action(self, action_market_create: ActionMarketCreate) -> ActionMarketDoc | None:
        try:
            action_market_doc_create = ActionMarketDocCreate(user_id=self.user_id, **action_market_create.model_dump())
            action_market_doc = await self.action_market_crud.insert_one(action_market_doc_create)
            return action_market_doc
        except Exception as e:
            log.exception(e)
        return None

    async def list_market_actions(
            self, action_market_find: ActionMarketFind, limit: int = 100, offset: int = 0
    ) -> List[ActionMarketDoc]:
        action_market_doc_find = ActionMarketDocFind(**action_market_find.model_dump())
        action_market_docs = await self.action_market_crud.find(action_market_doc_find, limit, offset)
        await UserActionMarket._mask_config_of_action_market_docs(action_market_docs)
        return action_market_docs

    async def get_market_action(self, market_action_id: str) -> ActionMarketDoc | None:
        try:
            action_market_doc_find = ActionMarketDocFind(id=market_action_id)
            action_market_docs = await self.action_market_crud.find(action_market_doc_find)
            if len(action_market_docs) != 1:
                raise HTTPException(500, "Error in finding action")
            await UserActionMarket._mask_config_of_action_market_docs(action_market_docs)
            return action_market_docs[0]
        except Exception as e:
            log.exception(e)
        return None

    async def update_market_action(
            self, market_action_id: str, market_action_update: ActionMarketUpdate
    ) -> ActionMarketDoc:
        action_market_doc_update = ActionMarketDocUpdate(
            id=market_action_id, user_id=self.user_id, **market_action_update.model_dump()
        )
        action_market_doc = await self.action_market_crud.update_one(action_market_doc_update)
        return action_market_doc

    async def delete_market_action(self, market_action_id: str) -> int:
        action_market_doc_find = ActionMarketDocFind(id=market_action_id, user_id=self.user_id)
        delete_result = await self.action_market_crud.delete_many(action_market_doc_find)
        return delete_result.deleted_count

    async def run_market_action(self, market_action_id: str, input: TextObj) -> Any:
        action_market_doc_find = ActionMarketDocFind(id=market_action_id)
        action_market_docs = await self.action_market_crud.find(action_market_doc_find)
        if len(action_market_docs) != 1:
            raise HTTPException(405, "Market Action cannot be run")
        resp = await ActionManager().run_action(action_market_docs[0].action, input)
        return resp

    @staticmethod
    async def _mask_config_of_action_market_docs(market_actions: List[ActionMarketDoc]) -> List[ActionMarketDoc]:
        for market_action in market_actions:
            market_action.action.config = {}
        return market_actions

    @staticmethod
    async def test_market_action(action_market_doc: ActionMarketDoc, input: TextObj) -> Any:
        resp = await ActionManager().run_action(action_market_doc.action, input)
        return resp
