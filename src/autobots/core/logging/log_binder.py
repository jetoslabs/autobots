from typing import Dict, Any

from src.autobots.core.logging.app_code import AppCode


class LogBinder:
    bind_dict: Dict[str, Any] = {}

    def __init__(self):
        self.bind_dict["app"] = "autobots"

    def with_kwargs(self, **kwargs):
        self.bind_dict.update(kwargs)
        return self

    def with_app_code(self, app_code: AppCode):
        self.bind_dict["app_code"] = app_code.value
        return self

    def with_action_graph_id(self, action_graph_id: str):
        self.bind_dict["action_graph_id"] = action_graph_id
        return self

    def with_action_graph_run_id(self, action_graph_run_id: str):
        self.bind_dict["action_graph_run_id"] = action_graph_run_id
        return self
    
    def with_action_id(self, action_id: str):
        self.bind_dict["action_id"] = action_id
        return self
    
    def with_action_run_id(self, action_run_id: str):
        self.bind_dict["action_run_id"] = action_run_id
        return self

    def get_bind_dict(self) -> Dict[str, Any]:
        return self.bind_dict

