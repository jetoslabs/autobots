from typing import List

from sqlalchemy import UUID
from sqlalchemy.orm import Session

from autobots.database.base import get_db
from autobots.database.database_models import PromptORM


class PromptCRUD:

    @staticmethod
    async def create(prompt: PromptORM, db: Session = next(get_db())) -> PromptORM:
        db.add(prompt)
        db.commit()
        db.refresh(prompt)
        return prompt

    @staticmethod
    async def read(user_id: UUID, id: UUID, db: Session = get_db()) -> List[PromptORM]:
        prompts = db.query(PromptORM) \
            .filter_by(user_id=user_id) \
            .filter_by(id=id) \
            .all()
        return prompts
        # session: SessionLocal = SessionLocal()
        # try:
        #     prompts = session.query(PromptORM) \
        #         .filter_by(user_id=user_id) \
        #         .filter_by(id=id) \
        #         .all()
        #     return prompts
        # finally:
        #     session.close()

    @staticmethod
    async def delete(prompt: PromptORM, db: Session = get_db()):
        db.delete(prompt)
        # session: SessionLocal = SessionLocal()
        # try:
        #     session.delete(prompt)
        #     session.commit()
        # finally:
        #     session.close()

    @staticmethod
    async def upsert(
            del_prompt: PromptORM,
            new_prompt: PromptORM,
            db: Session = get_db()
    ):
        await PromptCRUD.delete(del_prompt, db)
        await PromptCRUD.create(new_prompt, db)

    @staticmethod
    async def read_by_name(user_id: UUID, name: str, db: Session = get_db()) -> List[PromptORM]:
        prompts = db.query(PromptORM) \
            .filter_by(user_id=user_id) \
            .filter_by(name=name) \
            .all()
        return prompts
        # session: SessionLocal = SessionLocal()
        # try:
        #     prompts = session.query(PromptORM) \
        #         .filter_by(user_id=user_id) \
        #         .filter_by(name=name) \
        #         .all()
        #     return prompts
        # finally:
        #     session.close()
