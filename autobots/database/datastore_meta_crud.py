from typing import List

from sqlalchemy import UUID

from autobots.database.base import Session
from autobots.database.database_models import DatastoreMetaORM


class DatastoreMetaCRUD:

    @staticmethod
    async def create(datastore_meta: DatastoreMetaORM):
        session: Session = Session()
        try:
            session.add(datastore_meta)
            session.commit()
        finally:
            session.close()

    @staticmethod
    async def read(user_id: UUID, name: str) -> List[DatastoreMetaORM]:
        session: Session = Session()
        try:
            metas = session.query(DatastoreMetaORM) \
                .filter_by(user_id=user_id) \
                .filter_by(name=name) \
                .all()
            return metas
        finally:
            session.close()

    @staticmethod
    async def delete(datastore_meta: DatastoreMetaORM):
        session: Session = Session()
        try:
            session.delete(datastore_meta)
            session.commit()
        finally:
            session.close()

    @staticmethod
    async def upsert(
            del_datastore_meta: DatastoreMetaORM,
            new_datastore_meta: DatastoreMetaORM
    ):
        await DatastoreMetaCRUD.delete(del_datastore_meta)
        await DatastoreMetaCRUD.create(new_datastore_meta)

