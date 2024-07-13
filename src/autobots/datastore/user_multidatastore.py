import base64
import io
import re
import uuid
from PIL import Image
import os
import random
import string


from fastapi import HTTPException, UploadFile, BackgroundTasks
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import HttpUrl
from pymongo.results import DeleteResult
from src.autobots.api.webhook import Webhook
from src.autobots.conn.aws.s3 import S3, get_s3
from src.autobots.conn.pinecone.pinecone import Pinecone, get_pinecone
from src.autobots.conn.unstructured_io.unstructured_io import get_unstructured_io, PartitionParametersParams
from src.autobots.datastore.datastore_meta_crud import DatastoreMetaCRUD
from src.autobots.datastore.multidatastore import MultiDataStore
from src.autobots.datastore.datastore_meta_doc_model import DatastoreMetaDocCreate, DatastoreMetaDoc, DatastoreMetaDocFind
from src.autobots.datastore.datastore_result.datastore_result_doc_model import DatastoreResultCreate, DatastoreResultDoc, \
    DatastoreResultUpdate
from src.autobots.datastore.datastore_result.user_datastore_result import UserDatastoreResult
from src.autobots.event_result.event_result_model import EventResultStatus
from src.autobots.user.user_orm_model import UserORM


class UserDatastore():

    def __init__(self, user: UserORM, db: AsyncIOMotorDatabase, s3: S3 = get_s3(), pinecone: Pinecone = get_pinecone()):
        self.datastore = MultiDataStore(s3, pinecone, get_unstructured_io())
        self.user = user
        self.db = db
        self.datastore_meta_crud = DatastoreMetaCRUD(self.db)
        self.user_datastore_result = UserDatastoreResult(user, db)

    async def init(self, name: str) -> DatastoreMetaDoc:
        self.datastore.init(name)
        datastore_meta_doc_create = DatastoreMetaDocCreate(user_id=str(self.user.id), datastore_id=self.datastore.id,
                                                           name=self.datastore.name)
        user_datastore_meta = await self.datastore_meta_crud.insert_one(datastore_meta_doc_create)
        return user_datastore_meta

    async def hydrate(self, datastore_id: str) -> MultiDataStore:
        datastore_meta_doc_find = DatastoreMetaDocFind(user_id=str(self.user.id), datastore_id=datastore_id)
        datastore_metas = await self.datastore_meta_crud.find(datastore_meta_doc_find)
        if len(datastore_metas) != 1:
            raise HTTPException(404, "Datastore not found")
        datastore_meta = datastore_metas[0]
        datastore = self.datastore.hydrate(datastore_meta.datastore_id)
        return datastore