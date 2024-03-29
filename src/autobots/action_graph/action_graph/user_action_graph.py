from typing import List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, BackgroundTasks
from pymongo.database import Database

from src.autobots.action.action.common_action_models import TextObj
from src.autobots.action.action.user_actions import UserActions
from src.autobots.action.action_market.user_actions_market import UserActionsMarket
from src.autobots.action_graph.action_graph.action_graph import ActionGraph
from src.autobots.action_graph.action_graph_result.action_graph_result_model_doc import ActionGraphResultDoc
from src.autobots.action_graph.action_graph_result.user_action_graph_result import UserActionGraphResult
from src.autobots.api.webhook import Webhook
from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.action_graph.action_graph.action_graph_crud import ActionGraphCRUD
from src.autobots.action_graph.action_graph.action_graph_doc_model import ActionGraphCreate, ActionGraphDoc, \
    ActionGraphDocCreate, \
    ActionGraphFind, ActionGraphDocFind, ActionGraphUpdate, ActionGraphDocUpdate

from src.autobots.user.user_orm_model import UserORM


class UserActionGraphs:

    def __init__(self, user: UserORM, db: Database):
        self.user = user
        self.user_id = str(user.id)
        self.db = db

    async def create(
            self, action_graph_create: ActionGraphCreate, db: Database = Depends(get_mongo_db)
    ) -> ActionGraphDoc:
        action_graph_doc_create = ActionGraphDocCreate(user_id=self.user_id, **action_graph_create.model_dump())
        action_graph_doc = await ActionGraphCRUD(db).insert_one(action_graph_doc_create)
        return action_graph_doc

    async def list(
            self, action_graph_find: ActionGraphFind,
            db: Database = Depends(get_mongo_db),
            limit: int = 100, offset: int = 0
    ) -> List[ActionGraphDoc]:
        action_graph_doc_find = ActionGraphDocFind(user_id=self.user_id, **action_graph_find.model_dump())
        action_graph_docs = await ActionGraphCRUD(db).find(action_graph_doc_find, limit, offset)
        return action_graph_docs

    async def get(
            self, action_graph_id: str, db: Database = Depends(get_mongo_db)
    ) -> ActionGraphDoc:
        action_graph_doc_find = ActionGraphDocFind(id=action_graph_id, user_id=self.user_id)
        action_graph_docs = await ActionGraphCRUD(db).find(action_graph_doc_find)
        if len(action_graph_docs) != 1:
            raise HTTPException(500, "Error in finding action")
        return action_graph_docs[0]

    async def update(
            self, action_graph_id: str, action_graph_update: ActionGraphUpdate, db: Database = Depends(get_mongo_db)
    ) -> ActionGraphDoc:
        action_graph_doc_update = ActionGraphDocUpdate(id=action_graph_id, user_id=self.user_id,
                                                       **action_graph_update.model_dump())
        action_graph_doc = await ActionGraphCRUD(db).update_one(action_graph_doc_update)
        return action_graph_doc

    async def delete(
            self, action_graph_id: str, db: Database = Depends(get_mongo_db)
    ) -> int:
        action_graph_doc_find = ActionGraphDocFind(id=action_graph_id, user_id=self.user_id)
        delete_result = await ActionGraphCRUD(db).delete_many(action_graph_doc_find)
        return delete_result.deleted_count

    # async def run(
    #         self, action_graph_id: str, input: TextObj, db: Database = Depends(get_mongo_db)
    # ) -> Dict[str, Any]:
    #     action_graph_doc_find = ActionGraphDocFind(id=action_graph_id, user_id=self.user_id)
    #     action_docs = await ActionGraphCRUD(db).find(action_graph_doc_find)
    #     if len(action_docs) != 1:
    #         raise HTTPException(405, "Action Graph cannot be run")
    #     resp = await ActionGraph.run(self.user, input, action_docs[0].nodes, action_docs[0].graph, db)
    #     return resp

    async def run_in_background(
            self,
            user_actions: UserActions,
            user_actions_market: UserActionsMarket,
            user_action_graph_result: UserActionGraphResult,
            action_graph_id: str,
            input: TextObj,
            action_graph_result_id: Optional[str] = None,
            background_tasks: BackgroundTasks = None,
            webhook: Webhook | None = None,
    ) -> ActionGraphResultDoc | None:
        action_graph_doc = await self.get(action_graph_id, self.db)
        if not action_graph_doc:
            raise HTTPException(405, "Action Graph cannot be run")

        resp = await ActionGraph.run_in_background(
            action_graph_doc=action_graph_doc,
            action_graph_input_dict=input.model_dump(),
            user_actions=user_actions,
            user_actions_market=user_actions_market,
            user_action_graph_result=user_action_graph_result,
            action_graph_result_id=action_graph_result_id,
            background_tasks=background_tasks,
            webhook=webhook
        )
        return resp

    @staticmethod
    async def run_scheduled_action_graph(
            action_graph_id: str,
            user_id: str,
            input: TextObj,
            # background_tasks: BackgroundTasks = None, # Using Background thread will crash app
            action_graph_result_id: Optional[str] = None,
            webhook: Webhook | None = None,
            db: Database = next(get_mongo_db())
    ) -> ActionGraphResultDoc | None:
        user_orm = UserORM(id=UUID(user_id))
        user_actions = UserActions(user_orm, db)
        user_actions_market = UserActionsMarket(user_orm, db)
        user_action_graph_result = UserActionGraphResult(user_orm, db)
        resp = await UserActionGraphs(user=user_orm, db=db).run_in_background(
            user_actions=user_actions,
            user_actions_market=user_actions_market,
            user_action_graph_result=user_action_graph_result,
            action_graph_id=action_graph_id,
            input=input,
            action_graph_result_id=action_graph_result_id,
            # background_tasks,
            webhook=webhook
        )
        return resp