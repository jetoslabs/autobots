from typing import List

from fastapi import Depends
from sqlalchemy import UUID
from sqlalchemy.orm import Session

from autobots.database.base import get_db
from autobots.graphs.to_del.graph_orm_model import GraphORM


class GraphsCRUD:

    @staticmethod
    async def create(graph: GraphORM, db: Session = Depends(get_db)) -> GraphORM:
        db.add(graph)
        db.commit()
        db.refresh(graph)
        return graph

    @staticmethod
    async def list(
            user_id: UUID, limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
    ) -> List[GraphORM]:
        if limit < 0 or limit > 100:
            limit = 100
        if offset < 0:
            offset = 0
        graphs = db.query(GraphORM) \
            .filter_by(user_id=user_id) \
            .limit(limit) \
            .offset(offset * limit) \
            .all()
        return graphs

    @staticmethod
    async def read(user_id: UUID, id: UUID, db: Session = Depends(get_db)) -> GraphORM:
        graph = db.query(GraphORM) \
            .filter_by(user_id=user_id) \
            .filter_by(id=id) \
            .first()
        return graph

    @staticmethod
    async def delete(graph: GraphORM, db: Session = Depends(get_db)) -> GraphORM:
        db.delete(graph)
        db.commit()
        return graph

    @staticmethod
    async def upsert(
            del_graph: GraphORM,
            new_graph: GraphORM,
            db: Session = Depends(get_db)
    ) -> GraphORM:
        await GraphsCRUD.delete(del_graph, db)
        return await GraphsCRUD.create(new_graph, db)

    @staticmethod
    async def read_by_name_version(
            user_id: UUID,
            name: str, version: str = None,
            limit: int = 100, offset: int = 0,
            db: Session = Depends(get_db)
    ) -> List[GraphORM]:
        if limit < 0 or limit > 100:
            limit = 100
        if offset < 0:
            offset = 0

        query = db.query(GraphORM).filter_by(user_id=user_id).filter_by(name=name)
        if version:
            query.filter_by(version=version)
        query.limit(limit).offset(offset)
        prompts = query.all()
        return prompts

