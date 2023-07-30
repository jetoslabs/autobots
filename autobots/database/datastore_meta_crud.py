from typing import List

from sqlalchemy import UUID
from sqlalchemy.orm.session import Session

from autobots.database.base import get_db, SessionLocal
from autobots.database.database_models import DatastoreMetaORM


class DatastoreMetaCRUD:

    @staticmethod
    async def create(datastore_meta: DatastoreMetaORM, db: Session = get_db()):
        db.add(datastore_meta)
        # session = SessionLocal()
        # try:
        #     session.add(datastore_meta)
        #     session.commit()
        # finally:
        #     session.close()

    @staticmethod
    async def read(user_id: UUID, name: str, db: Session = get_db()) -> List[DatastoreMetaORM]:
        metas = db.query(DatastoreMetaORM) \
            .filter_by(user_id=user_id) \
            .filter_by(name=name) \
            .all()
        return metas
        # session: SessionLocal = SessionLocal()
        # try:
        #     metas = session.query(DatastoreMetaORM) \
        #         .filter_by(user_id=user_id) \
        #         .filter_by(name=name) \
        #         .all()
        #     return metas
        # finally:
        #     session.close()

    @staticmethod
    async def delete(datastore_meta: DatastoreMetaORM, db: Session = get_db()):
        db.delete(datastore_meta)
        # session: SessionLocal = SessionLocal()
        # try:
        #     session.delete(datastore_meta)
        #     session.commit()
        # finally:
        #     session.close()

    @staticmethod
    async def upsert(
            del_datastore_meta: DatastoreMetaORM,
            new_datastore_meta: DatastoreMetaORM,
            db: Session = get_db()
    ):
        await DatastoreMetaCRUD.delete(del_datastore_meta, db)
        await DatastoreMetaCRUD.create(new_datastore_meta, db)

