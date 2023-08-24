from typing import List

from bson import ObjectId
from fastapi import Depends, HTTPException
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import InsertOneResult, DeleteResult

from autobots.action.action_doc_model import ActionDoc, ActionDocCreate, ActionDocFind
from autobots.database.mongo_base import get_mongo_db


class ActionCRUD:

    def __init__(self, db: Database = Depends(get_mongo_db)):
        self.document: Collection = db[ActionDoc.__collection__]

    async def insert_one(self, action: ActionDocCreate) -> InsertOneResult:
        action_find = ActionDocFind(name=action.name, version=action.version, user_id=action.user_id)
        actions_found = await self.find(action_find)
        if len(actions_found) > 0:
            raise HTTPException(400, "Action name and version not unique")
        return self.document.insert_one(action.model_dump())

    async def find_by_object_id(self, id: str) -> ActionDoc:
        object_id = ObjectId(id)
        doc = self.document.find_one({"_id": object_id})
        doc["_id"] = str(doc.get("_id"))
        return ActionDoc.model_validate(doc)

    async def find(self, action: ActionDocFind) -> List[ActionDoc]:
        find_params = {}
        for key, value in action.model_dump().items():
            if value:
                if key == "id":
                    find_params["_id"] = ObjectId(value)
                else:
                    find_params[key] = value
        if len(find_params) == 0:
            return []

        cursor = self.document.find(find_params)
        action_docs = []
        for doc in cursor:
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

    async def upsert(self,):
        pass
