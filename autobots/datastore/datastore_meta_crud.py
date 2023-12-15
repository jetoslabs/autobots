from typing import List

from bson import ObjectId
from fastapi import HTTPException
from pymongo.collection import Collection, ReturnDocument
from pymongo.database import Database
from pymongo.results import DeleteResult

from autobots.core.logging.log import Log
from autobots.datastore.datastore_meta_doc_model import DatastoreMetaDoc, DatastoreMetaDocCreate, DatastoreMetaDocFind, \
    DatastoreMetaDocUpdate


class DatastoreMetaCRUD:

    def __init__(self, db: Database):
        self.document: Collection = db[DatastoreMetaDoc.__collection__]

    async def insert_one(self, datastore_meta_doc_create: DatastoreMetaDocCreate) -> DatastoreMetaDoc:
        datastore_meta_doc_find = DatastoreMetaDocFind(
            name=datastore_meta_doc_create.name, user_id=datastore_meta_doc_create.user_id
        )
        datastore_meta_doc_found = await self.find(datastore_meta_doc_find)
        if len(datastore_meta_doc_found) > 0:
            raise HTTPException(400, "Datastore_Meta not unique")
        insert_result = self.document.insert_one(datastore_meta_doc_create.model_dump())
        inserted_datastore_meta = await self._find_by_object_id(insert_result.inserted_id)
        return inserted_datastore_meta

    async def _find_by_object_id(self, id: str) -> DatastoreMetaDoc:
        object_id = ObjectId(id)
        doc = self.document.find_one({"_id": object_id})
        doc["_id"] = str(doc.get("_id"))
        return DatastoreMetaDoc.model_validate(doc)

    async def find(
            self, datastore_meta_doc_find: DatastoreMetaDocFind, limit: int = 100, offset: int = 0
    ) -> List[DatastoreMetaDoc]:
        find_params = {}
        for key, value in datastore_meta_doc_find.model_dump().items():
            if value is not None:
                if key == "id":
                    find_params["_id"] = ObjectId(value)
                else:
                    find_params[key] = value
        if len(find_params) == 0:
            return []

        cursor = self.document.find(find_params)
        datastore_meta_docs = []

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
                datastore_meta_doc = DatastoreMetaDoc.model_validate(doc)
                datastore_meta_docs.append(datastore_meta_doc)
            except Exception as e:
                Log.bind(action_doc=action_doc).error(f"Error while parsing action doc: {e}, skipping to next")

        return datastore_meta_docs

    async def delete_many(self, datastore_meta_doc_find: DatastoreMetaDocFind) -> DeleteResult:
        find_params = {}
        for key, value in datastore_meta_doc_find.model_dump().items():
            if value is not None:
                if key == "id":
                    find_params["_id"] = ObjectId(value)
                else:
                    find_params[key] = value

        delete_result = self.document.delete_many(find_params)
        return delete_result

    async def delete_one(self, id: str) -> DeleteResult:
        datastore_meta_doc = await self._find_by_object_id(id)
        if datastore_meta_doc is None:
            raise HTTPException(405, "Unable to find datastore_meta_doc to delete")
        delete_result = self.document.delete_one({"_id": ObjectId(datastore_meta_doc.id)})
        return delete_result

    async def update_one(self, datastore_meta_doc_update: DatastoreMetaDocUpdate) -> DatastoreMetaDoc:
        update_params = {}
        for key, value in datastore_meta_doc_update.model_dump().items():
            if value is not None:
                if key == "id":
                    update_params["_id"] = ObjectId(value)
                else:
                    update_params[key] = value
        if not update_params["_id"] and not update_params["user_id"]:
            raise HTTPException(405, "Cannot find datastore_meta_doc to update")

        updated_datastore_meta_doc = self.document.find_one_and_update(
            filter={"_id": update_params.get("_id"), "user_id": datastore_meta_doc_update.user_id},
            update={"$set": update_params},
            return_document=ReturnDocument.AFTER
        )
        if updated_datastore_meta_doc is None:
            raise HTTPException(405, "Unable to update datastore_meta_doc")

        updated_datastore_meta_doc["_id"] = str(updated_datastore_meta_doc.get("_id"))
        datastore_meta_doc = DatastoreMetaDoc.model_validate(updated_datastore_meta_doc)
        return datastore_meta_doc

    # @staticmethod
    # async def create(
    #         datastore_meta: DatastoreMetaORM, db: Session = Depends(get_db)
    # ) -> DatastoreMetaORM:
    #     db.add(datastore_meta)
    #     db.commit()
    #     db.refresh(datastore_meta)
    #     return datastore_meta

    # @staticmethod
    # async def list(
    #         user_id: UUID, limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
    # ) -> List[DatastoreMetaORM]:
    #     if limit < 0 or limit > 100:
    #         limit = 100
    #     if offset < 0:
    #         offset = 0
    #     datastore_meta = db.query(DatastoreMetaORM) \
    #         .filter_by(user_id=user_id) \
    #         .limit(limit) \
    #         .offset(offset * limit) \
    #         .all()
    #     return datastore_meta

    # @staticmethod
    # async def read_by_id(user_id: UUID, id: str, db: Session = Depends(get_db)) -> DatastoreMetaORM:
    #     datastore_meta = db.query(DatastoreMetaORM) \
    #         .filter_by(user_id=user_id) \
    #         .filter_by(id=id) \
    #         .first()
    #     return datastore_meta

    # @staticmethod
    # async def delete(datastore_meta: DatastoreMetaORM, db: Session = Depends(get_db)) -> DatastoreMetaORM:
    #     db.delete(datastore_meta)
    #     db.commit()
    #     return datastore_meta

    # @staticmethod
    # async def upsert(
    #         del_datastore_meta: DatastoreMetaORM,
    #         new_datastore_meta: DatastoreMetaORM,
    #         db: Session = Depends(get_db)
    # ) -> DatastoreMetaORM:
    #     await DatastoreMetaCRUD.delete(del_datastore_meta, db)
    #     return await DatastoreMetaCRUD.create(new_datastore_meta, db)

    # @staticmethod
    # async def read_by_name_version(
    #         user_id: UUID,
    #         name: str, version: str = None,
    #         limit: int = 100, offset: int = 0,
    #         db: Session = Depends(get_db)
    # ) -> List[DatastoreMetaORM]:
    #     if limit < 0 or limit > 100:
    #         limit = 100
    #     if offset < 0:
    #         offset = 0
    #
    #     query = db.query(DatastoreMetaORM).filter_by(user_id=user_id).filter_by(name=name)
    #     # if version:
    #     #     query.filter_by(version=version)
    #     query.limit(limit).offset(offset)
    #     datastore_meta = query.all()
    #     return datastore_meta
