import uuid

import pytest

from autobots.core.database.base import SessionLocal
from autobots.datastore.datastore_meta_orm_model import DatastoreMetaORM


@pytest.mark.asyncio
async def test_datastore_meta_happy_path(set_test_settings):
    session = SessionLocal()
    user_id = uuid.UUID("4d5d5063-36fb-422e-a811-cac8c2003d37")
    try:
        # # add user
        # user1 = UserORM(id=uuid.UUID("4d5d5063-36fb-422e-a811-cac8c2003d37"))
        # is_user_exist = session.query(UserORM)\
        #     .filter_by(id=user1.id)\
        #     .all()
        # if len(is_user_exist) == 0:
        #     session.add(user1)
        #     session.commit()

        # add datastore_meta
        name = "test_datastore_meta_happy_path"
        datastore_id = "teststore_halkdhfkssdfkjh"
        datastore_meta1 = DatastoreMetaORM(
            user_id=user_id,
            name=name,
            id=datastore_id
        )
        session.add(datastore_meta1)
        session.commit()

        # # query user
        # users = session.query(UserORM)\
        #     .filter_by(id=user1.id)\
        #     .all()
        # assert len(users) > 0
        # assert users[0].id == user1.id

        # query datastore_meta
        metas = session.query(DatastoreMetaORM) \
            .filter_by(user_id=user_id) \
            .filter_by(name=name)\
            .all()
        assert len(metas) > 0
        assert metas[0].user_id == user_id
        assert metas[0].name == name
        assert metas[0].id == datastore_id

        # # delete user
        # session.delete(users[0])
        # delete prompt
        session.delete(metas[0])
        # commit delete
        session.commit()

    except Exception as e:
        assert e is None

    finally:
        session.close()
