from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from autobots.core.log import log
from autobots.database.base import get_db
from autobots.graphs.to_del.graph import Graph
from autobots.graphs.to_del.graph_orm_model import GraphORM
from autobots.graphs.to_del.graphs_crud import GraphsCRUD
from autobots.prompts.user_prompts import Input
from autobots.user.user_orm_model import UserORM


class UserGraphCreateInput(BaseModel):
    name: str
    graph_map: Any #Dict[str, List[str]]
    version: Optional[float] = 0
    description: Optional[str] = ""


class UserGraphCreateOutput(UserGraphCreateInput):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserGraphs:

    def __init__(self, user: UserORM):
        self.user = user

    async def create(
            self, user_graph_create_input: UserGraphCreateInput, db: Session = Depends(get_db)
    ) -> GraphORM:
        graph = GraphORM(user_id=self.user.id, **user_graph_create_input.__dict__)
        graph_orm: GraphORM = await GraphsCRUD.create(graph, db)
        return graph_orm

    async def list(
            self, limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
    ) -> List[GraphORM]:
        if limit < 0 or limit > 100:
            limit = 100
        if offset < 0:
            offset = 0
        graphs = await GraphsCRUD.list(self.user.id, limit, offset, db)
        return graphs

    async def read(self, id: UUID, db: Session = Depends(get_db)) -> GraphORM:
        graph = await GraphsCRUD.read(self.user.id, id, db)
        return graph

    async def delete(self, id: UUID, db: Session = Depends(get_db)) -> GraphORM:
        existing_graph = await self.read(id, db)
        if self.user.id != existing_graph.user_id:
            raise HTTPException(405, "User does not own graph")
        graph_orm: GraphORM = await GraphsCRUD.delete(existing_graph, db)
        return graph_orm

    async def upsert(
            self, id: UUID, user_graph_create_input: UserGraphCreateInput, db: Session = Depends(get_db)
    ) -> GraphORM:
        existing_graph = await self.read(id, db)
        if self.user.id != existing_graph.user_id:
            raise HTTPException(405, "User does not own graph")
        new_graph = GraphORM(user_id=self.user.id, **user_graph_create_input.__dict__)
        graph_orm: GraphORM = await GraphsCRUD.upsert(existing_graph, new_graph, db)
        return graph_orm

    async def read_by_name_version(
            self, name: str, version: str = None, limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
    ) -> List[GraphORM]:
        graphs = await GraphsCRUD.read_by_name_version(self.user.id, name, version, limit, offset, db)
        return graphs

    async def run(self, input: Input, graph_id: UUID, db: Session = Depends(get_db)) -> Dict[str, str]:
        graph_orm: GraphORM = await self.read(graph_id, db)
        response = await Graph.run(self.user, input, graph_orm.graph_map, db)
        log.info(f"Graph run results: {response}")
        return response

    async def run_graph(self, input: Input, graph_map: Dict[str, List[str]], db: Session = Depends(get_db)) -> Dict[str, str]:
        response = await Graph.run(self.user, input, graph_map, db)
        log.info(f"Graph run results: {response}")
        return response
