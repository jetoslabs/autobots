from typing import List

from bson import ObjectId
from fastapi import Depends
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import DeleteResult

from autobots.action_run_log.action_run_log_doc_model import ActionRunLogDoc, ActionRunLogDocFind, ActionRunLog
from autobots.core.log import log
from autobots.database.mongo_base import get_mongo_db


class ActionRunLogCRUD:

    def __init__(self, db: Database = Depends(get_mongo_db)):
        self.document: Collection = db[ActionRunLogDoc.__collection__]

    async def insert_one(self, action_run_log: ActionRunLog) -> ActionRunLogDoc:
        insert_result = self.document.insert_one(action_run_log.model_dump())
        inserted_action = await self._find_by_object_id(insert_result.inserted_id)
        return inserted_action

    async def _find_by_object_id(self, id: str) -> ActionRunLogDoc:
        object_id = ObjectId(id)
        doc = self.document.find_one({"_id": object_id})
        doc["_id"] = str(doc.get("_id"))
        return ActionRunLogDoc.model_validate(doc)

    async def find(
            self, action_run_log_doc_find: ActionRunLogDocFind, limit: int = 100, offset: int = 0
    ) -> List[ActionRunLogDoc]:
        if not action_run_log_doc_find.action_user_id:
            log.error("action_run_log find issued without specifying user")
            return []
        find_params = {}
        for key, value in action_run_log_doc_find.model_dump().items():
            if value:
                if key == "id":
                    find_params["_id"] = ObjectId(value)
                elif key.startswith("action_"):
                    nested_key = key.replace("action_", "action.")
                    find_params[nested_key] = value
                else:
                    find_params[key] = value
        if len(find_params) == 0:
            return []

        cursor = self.document.find(find_params)
        action_run_log_docs = []

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
            action_run_log_doc = ActionRunLogDoc.model_validate(doc)
            action_run_log_docs.append(action_run_log_doc)

        return action_run_log_docs

    async def delete_many(self, action_run_log_doc_find: ActionRunLogDocFind) -> DeleteResult | None:
        if not action_run_log_doc_find.action_user_id:
            log.error("action_run_log delete issued without specifying user")
            return None
        find_params = {}
        for key, value in action_run_log_doc_find.model_dump().items():
            if value:
                if key == "id":
                    find_params["_id"] = ObjectId(value)
                elif key.startswith("action_"):
                    nested_key = key.replace("action_", "action.")
                    find_params[nested_key] = value
                else:
                    find_params[key] = value

        delete_result = self.document.delete_many(find_params)
        return delete_result

    # async def update_one(self, action_doc_update: ActionDocUpdate) -> ActionDoc:
    #     update_params = {}
    #     for key, value in action_doc_update.model_dump().items():
    #         if value:
    #             if key == "id":
    #                 update_params["_id"] = ObjectId(value)
    #             else:
    #                 update_params[key] = value
    #     if not update_params["_id"] and not update_params["user_id"]:
    #         raise HTTPException(405, "Cannot find action to update")
    #
    #     updated_action_doc = self.document.find_one_and_update(
    #         filter={"_id": update_params.get("_id"), "user_id": action_doc_update.user_id},
    #         update={"$set": update_params},
    #         return_document=ReturnDocument.AFTER
    #     )
    #     if updated_action_doc is None:
    #         raise HTTPException(405, "Unable to update action")
    #
    #     updated_action_doc["_id"] = str(updated_action_doc.get("_id"))
    #     action = ActionDoc.model_validate(updated_action_doc)
    #     return action

    # async def upsert(self, ):
    #     pass

