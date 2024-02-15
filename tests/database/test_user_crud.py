import uuid

import pytest

from src.autobots.core.database.base import get_db
from src.autobots.user.user_crud import UserCRUD
from src.autobots.user.user_orm_model import UserORM


@pytest.mark.asyncio
async def test_user_crud_happy_path(set_test_settings):
    user_id = uuid.UUID("4d5d5063-36fb-422e-a811-cac8c2003d37")
    try:
        with next(get_db()) as db:
            is_user_exist = await UserCRUD.read(user_id, db)
            if len(is_user_exist) == 0:
                # add user
                user1 = UserORM(id=user_id)
                await UserCRUD.create(user1, db)
                db.commit()

            # query user
            users = await UserCRUD.read(user_id, db)
            assert len(users) > 0
            assert users[0].id == user_id

            # delete user
            await UserCRUD.delete(users[0], db)
            db.commit()
            is_user_exist = await UserCRUD.read(user_id, db)
            assert len(is_user_exist) == 0

    except Exception as e:
        assert e is None
