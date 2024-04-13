from typing import List, Any, Dict

from fastapi import HTTPException
from loguru import logger
from pymongo.database import Database

from src.autobots.action.action.action_crud import ActionCRUD
from src.autobots.action.action.action_doc_model import ActionFind, ActionDocFind, ActionDoc, ActionDocCreate, ActionCreate, \
    ActionUpdate, ActionDocUpdate
from src.autobots.action.action_result.action_result_doc_model import ActionResultDoc
from src.autobots.action.action_result.user_action_result import UserActionResult
from src.autobots.action.action_type.action_factory import ActionFactory, RunActionObj
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.user.user_orm_model import UserORM


class UserActions:

    def __init__(self, user: UserORM, db: Database):
        self.user = user
        self.user_id = str(user.id)
        self.db = db
        self.action_crud = ActionCRUD(db)

    async def create_action(
            self, action_create: ActionCreate
    ) -> ActionDoc | None:
        try:
            # TODO: exclude_none=True
            # Create Config for the Action based on action type
            config = await ActionFactory.create_action_config(action_create.type, action_create.config)
            action_create.config = config
            # Now create Action
            action_doc_create = ActionDocCreate(user_id=self.user_id, **action_create.model_dump())
            action_doc = await self.action_crud.insert_one(action_doc_create)
            return action_doc
        except HTTPException as e:
            logger.error(str(e))
            raise
        except Exception as e:
            logger.exception(str(e))
            raise

    async def list_actions(
            self, action_find: ActionFind,
            limit: int = 100, offset: int = 0
    ) -> List[ActionDoc]:
        action_doc_find = ActionDocFind(user_id=self.user_id, **action_find.model_dump())
        action_docs = await self.action_crud.find(action_doc_find, limit, offset)
        return action_docs

    async def get_action(
            self, action_id: str
    ) -> ActionDoc | None:
        try:
            action_doc_find = ActionDocFind(id=action_id, user_id=self.user_id)
            action_docs = await self.action_crud.find(action_doc_find)
            if len(action_docs) != 1:
                raise HTTPException(500, "Error in finding action")
            return action_docs[0]
        except Exception as e:
            logger.error(str(e))
        return None

    async def update_action(
            self, action_id: str, action_update: ActionUpdate
    ) -> ActionDoc:
        if action_update.config:
            # Update Config for the Action based on action type
            existing_action_doc = await self.get_action(action_id)
            updated_config = await ActionFactory.update_action_config(
                existing_action_doc.type, existing_action_doc.config, action_update.config
            )
            action_update.config = updated_config
        # Now create Action
        action_doc_update = ActionDocUpdate(id=action_id, user_id=self.user_id, **action_update.model_dump())
        action_doc = await self.action_crud.update_one(action_doc_update)
        return action_doc

    async def delete_action(
            self, action_id: str
    ) -> int:
        action_doc_find = ActionDocFind(id=action_id, user_id=self.user_id)
        delete_result = await self.action_crud.delete_many(action_doc_find)
        return delete_result.deleted_count

    async def run_action(
            self, action_id: str, input: Dict[str, Any]
    ) -> Any:
        action_doc_find = ActionDocFind(id=action_id, user_id=self.user_id)
        action_docs = await self.action_crud.find(action_doc_find)
        if len(action_docs) != 1:
            raise HTTPException(405, "Action cannot be run")
        resp: RunActionObj = await ActionFactory.run_action(action_docs[0], input)
        return resp.output_dict

    async def run_action_v1(
            self, action_id: str, input: Dict[str, Any], action_result_id: str = None
    ) -> ActionDoc:
        if action_id == "":
            action_doc = ActionDoc(
                id="", user_id=self.user_id, name="", type=ActionType.mock_action, input=input, output={"texts":[input]}
            )
            return action_doc

        action_doc_find = ActionDocFind(id=action_id, user_id=self.user_id)
        action_docs = await self.action_crud.find(action_doc_find)
        if len(action_docs) != 1:
            raise HTTPException(405, "Action not found")
        action_doc = action_docs[0]
        action_doc.input = input

        if action_result_id is not None:
            user_action_result = UserActionResult(self.user, self.db)
            action_result_doc:  ActionResultDoc | None = await user_action_result.get_action_result(action_result_id)
            if action_result_doc is None:
                raise HTTPException(405, "Action Result not found")
            # action_result_doc.result.input

        resp: RunActionObj = await ActionFactory.run_action(action_doc, input)
        action_doc.output = resp.output_dict
        return action_doc

    @staticmethod
    async def run_action_doc(action_doc: ActionDoc, input: Dict[str, Any]) -> ActionDoc:
        action_doc.input = input
        resp: RunActionObj = await ActionFactory.run_action(action_doc, input)
        action_doc.output = resp.output_dict
        return action_doc
