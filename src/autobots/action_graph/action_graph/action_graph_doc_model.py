from datetime import datetime
from typing import Dict, List, Optional

from pydantic import Field, BaseModel, ConfigDict
from pydantic_extra_types.pendulum_dt import DateTime

from src.autobots.action.action.action_doc_model import ActionDoc
from src.autobots.action.action.common_action_models import TextObj
from src.autobots.core.database.mongo_base_crud import DocFindPage
from src.autobots.data_model.updated_at import UpdatedAt


class Position(BaseModel):
    x: int
    y: int


class NodeData(BaseModel):
    label: str
    actionId: str
    user_review_required: bool = False
    user_review_done: bool = False


class Node(BaseModel):
    id: str
    position: Optional[Position] = None
    type: Optional[str] = None
    data: NodeData


class ActionGraphFind(BaseModel):
    """
    Input from User to find action_graph
    """
    id: Optional[str] = Field(default=None)  # , alias='_id')
    name: Optional[str] = None
    version: Optional[float] = None
    description: Optional[str] = None
    is_published: Optional[bool] = None


class ActionGraphDocFind(ActionGraphFind):
    """
    Add in user id to enforce multi-tenancy
    """
    user_id: str


class ActionGraphPublishedDocFind(ActionGraphDocFind):
    user_id: str | None = None
    is_published: bool = True


class ActionGraphUpdate(BaseModel):
    name: Optional[str] = None
    version: Optional[float] = None
    description: Optional[str] = None
    nodes: Optional[Dict[str, str]] = Field(None, description="map of node to action",
                                            examples=[{"node1": "action1", "node2": "action2", "node3": "action3"}])
    node_details: Dict[str, Node] | None = Field(None, description="map of nodeId to Node",
                                                 examples=[{"node1": {"id": "node1", "position": {"x": 288, "y": 203},
                                                                      "type": "default",
                                                                      "data": {"label": "action1_name_version",
                                                                               "actionId": "action1"}}}])
    graph: Optional[Dict[str, List[str]]] = Field(None, description="map of node to nodes",
                                                  examples=[{"node1": ["node2", "node3"], "node2": ["node3"]}])
    start_node_id: str | None = None
    input: Optional[TextObj] = None
    output: Optional[Dict[str, ActionDoc]] = None
    is_published: Optional[bool] = None


class ActionGraphDocUpdate(ActionGraphUpdate, UpdatedAt):
    id: str
    user_id: str
    # updated_at: datetime = datetime.now()


class ActionGraphCreate(BaseModel):
    """
    Input from User to create action_graph
    """
    name: str
    version: float = 0
    description: str = ""
    nodes: Optional[Dict[str, str]] = Field(None, description="map of node to action",
                                            examples=[{"node1": "action1", "node2": "action2", "node3": "action3"}])
    node_details: Dict[str, Node] | None = Field(None, description="map of nodeId to Node",
                                                 examples=[{"node1": {"id": "node1", "position": {"x": 288, "y": 203},
                                                                      "type": "default",
                                                                      "data": {"label": "action1_name_version",
                                                                               "actionId": "action1"}}}])
    graph: Optional[Dict[str, List[str]]] = Field(None, description="map of node to nodes",
                                                  examples=[{"node1": ["node2", "node3"], "node2": ["node3"]}])
    start_node_id: str | None = None
    input: Optional[TextObj] = None
    output: Optional[Dict[str, ActionDoc]] = None
    is_published: bool = False


class ActionGraphDocCreate(ActionGraphCreate, UpdatedAt):
    """
    Add in user id to enforce multi-tenancy
    """
    user_id: str
    created_at: datetime = datetime.now()
    # updated_at: datetime = datetime.now()


class ActionGraphDoc(ActionGraphDocCreate):
    __collection__ = "ActionGraphs"

    id: str = Field(..., alias='_id')

    model_config = ConfigDict(populate_by_name=True)


class ActionGraphLiteDoc(BaseModel):
    id: str = Field(..., alias='_id')
    name: str
    version: float = 0
    description: str = ""
    is_published: bool = False
    user_id: str
    created_at: datetime
    updated_at: DateTime

    model_config = ConfigDict(populate_by_name=True)


class ActionGraphDocsFound(DocFindPage):
    docs: List[ActionGraphLiteDoc]
