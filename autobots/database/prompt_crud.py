from typing import List

from fastapi import Depends
from sqlalchemy import UUID
from sqlalchemy.orm import Session

from autobots.database.base import get_db
from autobots.database.database_models import PromptORM


class PromptCRUD:

    @staticmethod
    async def create(prompt: PromptORM, db: Session = Depends(get_db)) -> PromptORM:
        db.add(prompt)
        db.commit()
        db.refresh(prompt)
        return prompt

    @staticmethod
    async def list(
            user_id: UUID, limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
    ) -> List[PromptORM]:
        if limit < 0 or limit > 100:
            limit = 100
        if offset < 0:
            offset = 0
        prompts = db.query(PromptORM) \
            .filter_by(user_id=user_id) \
            .limit(limit) \
            .offset(offset * limit) \
            .all()
        return prompts

    @staticmethod
    async def read(user_id: UUID, id: UUID, db: Session = Depends(get_db)) -> PromptORM:
        prompt = db.query(PromptORM) \
            .filter_by(user_id=user_id) \
            .filter_by(id=id) \
            .first()
        return prompt

    @staticmethod
    async def delete(prompt: PromptORM, db: Session = Depends(get_db)) -> PromptORM:
        db.delete(prompt)
        db.commit()
        return prompt

    @staticmethod
    async def upsert(
            del_prompt: PromptORM,
            new_prompt: PromptORM,
            db: Session = Depends(get_db)
    ) -> PromptORM:
        await PromptCRUD.delete(del_prompt, db)
        return await PromptCRUD.create(new_prompt, db)

    @staticmethod
    async def read_by_name_version(
            user_id: UUID,
            name: str, version: str = None,
            limit: int = 100, offset: int = 0,
            db: Session = Depends(get_db)
    ) -> List[PromptORM]:
        if limit < 0 or limit > 100:
            limit = 100
        if offset < 0:
            offset = 0

        query = db.query(PromptORM).filter_by(user_id=user_id).filter_by(name=name)
        if version:
            query.filter_by(version=version)
        query.limit(limit).offset(offset)
        prompts = query.all()
        return prompts
