from typing import List

from bson import ObjectId
from fastapi import Depends
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import DESCENDING

from src.autobots.action.action.action_doc_model import ActionDoc
from src.autobots.action.action_market.action_market_model import ActionMarketDocFind
from src.autobots.core.database.mongo_base import get_mongo_db


class ActionMarketCRUD:

    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
        self.document: AsyncIOMotorCollection = db[ActionDoc.__collection__]

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
        cursor.sort([("updated_at", DESCENDING), ("created_at", DESCENDING)]).skip(offset).limit(limit)
        action_docs = []

        skipped = 0
        filled = 0
        async for doc in cursor:
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
                logger.bind(action_doc=action_doc).error(f"Error while parsing action doc: {e}, skipping to next")

        return action_docs

