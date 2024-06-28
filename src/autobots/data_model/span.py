from enum import Enum


class Span(Enum, str):
    Conn = "conn"

    Action = "action"
    ActionCreate = "action_create"
    ActionRead = "action_read"
    ActionUpdate = "action_update"
    ActionDelete = "action_delete"
    ActionRun = "action_run"
    ActionRerun = "action_rerun"

    ActionGraph = "action_graph"
    ActionGraphCreate = "action_graph_create"
    ActionGraphRead = "action_graph_read"
    ActionGraphUpdate = "action_graph_update"
    ActionGraphDelete = "action_graph_delete"
    ActionGraphRun = "action_graph_run"
    ActionGraphRerun = "action_graph_rerun"
    ActionGraphNodeRerun = "action_graph_node_rerun"



