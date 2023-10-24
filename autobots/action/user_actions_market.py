from typing import List, Dict, Any

from pymongo.database import Database

from autobots.action.action_crud import ActionCRUD
from autobots.action.action_doc_model import ActionFind, ActionDoc, ActionDocFind
from autobots.action.user_actions import UserActions
from autobots.user.user_orm_model import UserORM


class UserActionsMarket:

    def __init__(self, user: UserORM, db: Database):
        self.user = user
        self.user_id = str(user.id)
        self.action_crud = ActionCRUD(db)
        self._user_actions = UserActions(user, db)


    async def create_market_action(self):
        pass

    async def list_market_actions(
            self, action_find: ActionFind,
            limit: int = 100, offset: int = 0
    ) -> List[ActionDoc]:
        # Market actions will have `is_published = True`
        action_find.is_published = True
        action_doc_find = ActionDocFind(**action_find.model_dump())
        action_docs = await self.action_crud.find(action_doc_find, limit, offset)
        published_actions = []
        for action_doc in action_docs:
            action_doc.config = {}
            published_actions.append(action_doc)
        return published_actions


    async def get_market_action(self):
        pass


    async def run_market_action(
            self, action_id: str, input: Dict[str, Any]
    ) -> Any:
        # Only get action if it is published in market
        # Market actions will have `is_published = True`
        action_find = ActionFind(id=action_id, is_published=True)
        action_doc_find = ActionDocFind(**action_find.model_dump())
        action_docs = await self.action_crud.find(action_doc_find, 1, 0)
        action_doc = action_docs[0]
        resp = await self._user_actions.run_action_doc(action_doc, input)
        return resp
