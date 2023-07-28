from typing import List

from sqlalchemy import UUID

from autobots.database.base import Session
from autobots.database.database_models import PromptORM


class PromptCRUD:

    @staticmethod
    async def create(prompt: PromptORM):
        session: Session = Session()
        try:
            session.add(prompt)
            session.commit()
        finally:
            session.close()

    @staticmethod
    async def read(user_id: UUID, id: UUID) -> List[PromptORM]:
        session: Session = Session()
        try:
            prompts = session.query(PromptORM) \
                .filter_by(user_id=user_id) \
                .filter_by(id=id) \
                .all()
            return prompts
        finally:
            session.close()

    @staticmethod
    async def delete(prompt: PromptORM):
        session: Session = Session()
        try:
            session.delete(prompt)
            session.commit()
        finally:
            session.close()

    @staticmethod
    async def upsert(
            del_prompt: PromptORM,
            new_prompt: PromptORM
    ):
        await PromptCRUD.delete(del_prompt)
        await PromptCRUD.create(new_prompt)

    @staticmethod
    async def read_by_name(user_id: UUID, name: str) -> List[PromptORM]:
        session: Session = Session()
        try:
            prompts = session.query(PromptORM) \
                .filter_by(user_id=user_id) \
                .filter_by(name=name) \
                .all()
            return prompts
        finally:
            session.close()
