from typing import List

from sqlalchemy import UUID
from sqlalchemy.orm import Session

from autobots.core.database.base import get_db
from autobots.user.user_orm_model import UserORM


# TODO
class UserCRUD:

    @staticmethod
    async def create(user: UserORM, db: Session = next(get_db())):
        db.add(user)

    @staticmethod
    async def read(id: UUID, db: Session = next(get_db())) -> List[UserORM]:
        users = db.query(UserORM) \
            .filter_by(id=id) \
            .all()
        return users

    @staticmethod
    async def delete(user: UserORM, db: Session = next(get_db())):
        db.delete(user)

    @staticmethod
    async def upsert(
            del_user: UserORM,
            new_user: UserORM,
            db: Session = next(get_db())
    ):
        await UserCRUD.delete(del_user, db)
        await UserCRUD.create(new_user, db)
