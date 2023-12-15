from typing import List

from bson import ObjectId
from fastapi import Depends
from pymongo.collection import Collection
from pymongo.database import Database

from autobots.action.action.action_doc_model import ActionDoc
from autobots.action.action_market.action_market_model import ActionMarketDocFind
from autobots.core.database.mongo_base import get_mongo_db
from autobots.core.logging.log import Log


class ActionMarketCRUD:

    def __init__(self, db: Database = Depends(get_mongo_db)):
        self.document: Collection = db[ActionDoc.__collection__]

    async def find(
            self, action_market_doc_find: ActionMarketDocFind, limit: int = 100, offset: int = 0
    ) -> List[ActionDoc]:
        find_params = {}
        for key, value in action_market_doc_find.model_dump().items():
            if value is not None:
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
            action_doc = None
            try:
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
            except Exception as e:
                Log.bind(action_doc=action_doc).error(f"Error while parsing action doc: {e}, skipping to next")

        return action_docs

