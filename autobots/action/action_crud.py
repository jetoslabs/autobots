from typing import List

from bson import ObjectId
from fastapi import Depends, HTTPException
from pymongo.collection import Collection, ReturnDocument
from pymongo.database import Database
from pymongo.results import DeleteResult

from autobots.action.action_doc_model import ActionDoc, ActionDocCreate, ActionDocFind, ActionDocUpdate
from autobots.database.mongo_base import get_mongo_db


class ActionCRUD:

    def __init__(self, db: Database = Depends(get_mongo_db)):
        self.document: Collection = db[ActionDoc.__collection__]

    async def insert_one(self, action: ActionDocCreate) -> ActionDoc:
        action_find = ActionDocFind(name=action.name, version=action.version, user_id=action.user_id)
        actions_found = await self.find(action_find)
        if len(actions_found) > 0:
            raise HTTPException(400, "Action name and version not unique")
        insert_result = self.document.insert_one(action.model_dump())
        inserted_action = await self._find_by_object_id(insert_result.inserted_id)
        return inserted_action

    async def _find_by_object_id(self, id: str) -> ActionDoc:
        object_id = ObjectId(id)
        doc = self.document.find_one({"_id": object_id})
        doc["_id"] = str(doc.get("_id"))
        return ActionDoc.model_validate(doc)

    async def find(
            self, action_doc_find: ActionDocFind, limit: int = 100, offset: int = 0
    ) -> List[ActionDoc]:
        find_params = {}
        for key, value in action_doc_find.model_dump().items():
            if value:
                if key == "id":
                    find_params["_id"] = ObjectId(value)
                else:
                    find_params[key] = value
        if len(find_params) == 0:
            return []

        cursor = self.document.find(find_params)
        action_docs = []

        skipped = 0
        filled = 0
        for doc in cursor:
            # skipping records
            if skipped < offset * limit:
                skipped = skipped + 1
                continue
            # break if limit reached
            if filled >= limit:
                break
            filled = filled + 1
            # Mongo Result field _id has ObjectId, converting it to str for pydantic model
            doc["_id"] = str(doc.get("_id"))
            action_doc = ActionDoc.model_validate(doc)
            action_docs.append(action_doc)

        return action_docs

    async def delete_many(self, action: ActionDocFind) -> DeleteResult:
        find_params = {}
        for key, value in action.model_dump().items():
            if value:
                if key == "id":
                    find_params["_id"] = ObjectId(value)
                else:
                    find_params[key] = value

        delete_result = self.document.delete_many(find_params)
        return delete_result

    async def update_one(self, action_doc_update: ActionDocUpdate) -> ActionDoc:
        update_params = {}
        for key, value in action_doc_update.model_dump().items():
            if value:
                if key == "id":
                    update_params["_id"] = ObjectId(value)
                else:
                    update_params[key] = value
        if not update_params["_id"] and not update_params["user_id"]:
            raise HTTPException(405, "Cannot find action to update")

        updated_action_doc = self.document.find_one_and_update(
            filter={"_id": update_params.get("_id"), "user_id": action_doc_update.user_id},
            update={"$set": update_params},
            return_document=ReturnDocument.AFTER
        )
        if updated_action_doc is None:
            raise HTTPException(405, "Unable to update action")

        updated_action_doc["_id"] = str(updated_action_doc.get("_id"))
        action = ActionDoc.model_validate(updated_action_doc)
        return action

    async def upsert(self, ):
        pass

