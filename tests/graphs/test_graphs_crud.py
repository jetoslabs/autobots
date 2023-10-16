import uuid

import pytest

from autobots.database.base import get_db
from autobots.graphs.to_del.graph_orm_model import GraphORM
from autobots.graphs.to_del.graphs_crud import GraphsCRUD


@pytest.mark.asyncio
async def test_graphs_crud_happy_path(set_test_settings):
    user_id = uuid.UUID("4d5d5063-36fb-422e-a811-cac8c2003d37")

    name = "test_graphs_crud_happy_path"
    graph_map = {
        "node1": ["node2", "node3"],
        "node2": ["node3", "node4"]
    }
    graph_orm = GraphORM(
        name=name,
        graph_map=graph_map,
        user_id=user_id
    )

    with next(get_db()) as db:
        graph = await GraphsCRUD.create(graph_orm, db)

        assert graph.id is not ""
        assert graph.graph_map.get("node2") == ["node3", "node4"]

        await GraphsCRUD.delete(graph, db)
