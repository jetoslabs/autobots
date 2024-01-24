from typing import List

from bson import ObjectId
from fastapi import Depends, HTTPException
from pymongo.collection import Collection, ReturnDocument
from pymongo.database import Database
from pymongo.results import DeleteResult

from src.autobots.action.action_chat.chat_doc_model import ChatDoc, ChatDocCreate, ChatDocFind, ChatDocUpdate
from src.autobots.conn.openai.openai_chat.chat_model import Message
from src.autobots.core.database.mongo_base import get_mongo_db


class ChatCRUD:

    def __init__(self, db: Database = Depends(get_mongo_db)):
        self.document: Collection = db[ChatDoc.__collection__]

    async def insert_one(self, chat: ChatDocCreate) -> ChatDoc:
        insert_result = self.document.insert_one(chat.model_dump())
        inserted_chat = await self._find_by_object_id(insert_result.inserted_id)
        return inserted_chat

    async def _find_by_object_id(self, id: str) -> ChatDoc:
        object_id = ObjectId(id)
        doc = self.document.find_one({"_id": object_id})
        doc["_id"] = str(doc.get("_id"))
        return ChatDoc.model_validate(doc)

    async def find(
            self, chat_doc_find: ChatDocFind, limit: int = 100, offset: int = 0
    ) -> List[ChatDoc]:
        find_params = {}
        for key, value in chat_doc_find.model_dump().items():
            if value is not None:
                if key == "id":
                    find_params["_id"] = ObjectId(value)
                else:
                    find_params[key] = value
        if len(find_params) == 0:
            return []

        cursor = self.document.find(find_params)
        chat_docs = []

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
            chat_doc = ChatDoc.model_validate(doc)
            chat_docs.append(chat_doc)

        return chat_docs

    async def delete_many(self, chat: ChatDocFind) -> DeleteResult:
        find_params = {}
        for key, value in chat.model_dump().items():
            if value is not None:
                if key == "id":
                    find_params["_id"] = ObjectId(value)
                else:
                    find_params[key] = value

        delete_result = self.document.delete_many(find_params)
        return delete_result

    async def update_one(self, chat_doc_update: ChatDocUpdate) -> ChatDoc:
        update_params = {}
        for key, value in chat_doc_update.model_dump().items():
            if value is not None:
                if key == "id":
                    update_params["_id"] = ObjectId(value)
                else:
                    update_params[key] = value
        if not update_params["_id"] and not update_params["user_id"]:
            raise HTTPException(405, "Cannot find chat to update")

        updated_chat_doc = self.document.find_one_and_update(
            filter={"_id": update_params.get("_id"), "user_id": chat_doc_update.user_id},
            update={"$set": update_params},
            return_document=ReturnDocument.AFTER
        )
        if updated_chat_doc is None:
            raise HTTPException(405, "Unable to update chat")

        updated_chat_doc["_id"] = str(updated_chat_doc.get("_id"))
        chat = ChatDoc.model_validate(updated_chat_doc)
        return chat

    async def _append_message(self, messages: List[Message]):
        pass



