
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from src.autobots.core.database.mongo_base import get_mongo_db
from src.autobots.action_graph.action_graph.action_graph_doc_model import ActionGraphDoc, ActionGraphDocCreate, \
    ActionGraphDocFind, \
    ActionGraphDocUpdate, ActionGraphLiteDoc
from src.autobots.core.database.mongo_base_crud import CRUDBase


class ActionGraphCRUD(
    CRUDBase[ActionGraphDoc, ActionGraphLiteDoc, ActionGraphDocCreate, ActionGraphDocFind, ActionGraphDocUpdate]
):

    def __init__(self, db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
        self.document: AsyncIOMotorCollection = db[ActionGraphDoc.__collection__]
        super().__init__(ActionGraphDoc, ActionGraphLiteDoc, self.document)

    # async def insert_one(self, action_graph: ActionGraphDocCreate) -> ActionGraphDoc:
    #     action_graph_find = ActionGraphDocFind(name=action_graph.name, version=action_graph.version,
    #                                            user_id=action_graph.user_id)
    #     actions_graph_found = await self.find_one(action_graph_find)
    #     if actions_graph_found:
    #         raise HTTPException(400, "Action name and version not unique")
    #     insert_result = await self.document.insert_one(action_graph.model_dump())
    #     inserted_action_graph = await self.find_by_id(insert_result.inserted_id)
    #     return inserted_action_graph

    # async def get_by_object_id(self, id: str) -> ActionGraphDoc:
    #     object_id = ObjectId(id)
    #     doc = await self.document.find_one({"_id": object_id})
    #     doc["_id"] = str(doc.get("_id"))
    #     return ActionGraphDoc.model_validate(doc)

    # async def find(
    #         self, action_graph_doc_find: ActionGraphDocFind, limit: int = 100, offset: int = 0
    # ) -> List[ActionGraphDoc]:
    #     find_params = {}
    #     for key, value in action_graph_doc_find.model_dump().items():
    #         if value is not None:
    #             if key == "id":
    #                 find_params["_id"] = ObjectId(value)
    #             else:
    #                 find_params[key] = value
    #     if len(find_params) == 0:
    #         return []
    #
    #     cursor = self.document.find(find_params)
    #     cursor.sort([("updated_at", DESCENDING), ("created_at", DESCENDING)]).skip(offset).limit(limit)
    #     action_graph_docs = []
    #
    #     skipped = 0
    #     filled = 0
    #     async for doc in cursor:
    #         # skipping records
    #         if skipped < offset * limit:
    #             skipped = skipped + 1
    #             continue
    #         # break if limit reached
    #         if filled >= limit:
    #             break
    #         filled = filled + 1
    #         # Mongo Result field _id has ObjectId, converting it to str for pydantic model
    #         doc["_id"] = str(doc.get("_id"))
    #         action_doc = ActionGraphDoc.model_validate(doc)
    #         action_graph_docs.append(action_doc)
    #
    #     return action_graph_docs

    # async def delete_many(self, action_graph: ActionGraphDocFind) -> DeleteResult:
    #     find_params = {}
    #     for key, value in action_graph.model_dump().items():
    #         if value is not None:
    #             if key == "id":
    #                 find_params["_id"] = ObjectId(value)
    #             else:
    #                 find_params[key] = value
    #
    #     delete_result = await self.document.delete_many(find_params)
    #     return delete_result

    # async def update_one(self, action_graph_doc_update: ActionGraphDocUpdate) -> ActionGraphDoc:
    #     update_params = {}
    #     for key, value in action_graph_doc_update.model_dump().items():
    #         if value is not None:
    #             if key == "id":
    #                 update_params["_id"] = ObjectId(value)
    #             else:
    #                 update_params[key] = value
    #     if not update_params["_id"] and not update_params["user_id"]:
    #         raise HTTPException(405, "Cannot find action to update")
    #
    #     updated_action_graph_doc = await self.document.find_one_and_update(
    #         filter={"_id": update_params.get("_id"), "user_id": action_graph_doc_update.user_id},
    #         update={"$set": update_params},
    #         return_document=ReturnDocument.AFTER
    #     )
    #     if updated_action_graph_doc is None:
    #         raise HTTPException(405, "Unable to update action")
    #
    #     updated_action_graph_doc["_id"] = str(updated_action_graph_doc.get("_id"))
    #     action = ActionGraphDoc.model_validate(updated_action_graph_doc)
    #     return action

    # async def upsert(self, ):
    #     pass
