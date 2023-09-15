from typing import List

from fastapi import Depends
from sqlalchemy import UUID
from sqlalchemy.orm.session import Session

from autobots.database.base import get_db, SessionLocal
from autobots.datastore.datastore_meta_orm_model import DatastoreMetaORM


class DatastoreMetaCRUD:

    @staticmethod
    async def create(
            datastore_meta: DatastoreMetaORM, db: Session = Depends(get_db)
    ) -> DatastoreMetaORM:
        db.add(datastore_meta)
        db.commit()
        db.refresh(datastore_meta)
        return datastore_meta

    @staticmethod
    async def list(
            user_id: UUID, limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
    ) -> List[DatastoreMetaORM]:
        if limit < 0 or limit > 100:
            limit = 100
        if offset < 0:
            offset = 0
        datastore_meta = db.query(DatastoreMetaORM) \
            .filter_by(user_id=user_id) \
            .limit(limit) \
            .offset(offset * limit) \
            .all()
        return datastore_meta

    @staticmethod
    async def read_by_id(user_id: UUID, id: str, db: Session = Depends(get_db)) -> DatastoreMetaORM:
        datastore_meta = db.query(DatastoreMetaORM) \
            .filter_by(user_id=user_id) \
            .filter_by(id=id) \
            .first()
        return datastore_meta

    @staticmethod
    async def delete(datastore_meta: DatastoreMetaORM, db: Session = Depends(get_db)) -> DatastoreMetaORM:
        db.delete(datastore_meta)
        db.commit()
        return datastore_meta

    @staticmethod
    async def upsert(
            del_datastore_meta: DatastoreMetaORM,
            new_datastore_meta: DatastoreMetaORM,
            db: Session = Depends(get_db)
    ) -> DatastoreMetaORM:
        await DatastoreMetaCRUD.delete(del_datastore_meta, db)
        return await DatastoreMetaCRUD.create(new_datastore_meta, db)

    @staticmethod
    async def read_by_name_version(
            user_id: UUID,
            name: str, version: str = None,
            limit: int = 100, offset: int = 0,
            db: Session = Depends(get_db)
    ) -> List[DatastoreMetaORM]:
        if limit < 0 or limit > 100:
            limit = 100
        if offset < 0:
            offset = 0

        query = db.query(DatastoreMetaORM).filter_by(user_id=user_id).filter_by(name=name)
        # if version:
        #     query.filter_by(version=version)
        query.limit(limit).offset(offset)
        datastore_meta = query.all()
        return datastore_meta
