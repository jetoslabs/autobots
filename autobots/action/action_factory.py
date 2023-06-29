from typing import Dict, Tuple, Any

from autobots.action.action import Action, ActionData


class ActionFactory:

    def __init__(self):
        self.actions: Dict[str, (Action, ActionData)] = {}
        # self.actions_data: Dict[str, ActionData] = {}

    async def register(self, action_name: str, action_class: Any, action_data_class: Any) -> bool:
        self.actions[action_name] = (action_class, action_data_class)
        # self.actions_data[action_name] = action_data
        return True

    async def get_action_classes(self, action_name: str) -> Tuple[Any, Any]:
        return self.actions.get(action_name)

    async def run_action(self, action: Action, action_data: ActionData) -> ActionData:
        action_data = await action.run(action_data)
        return action_data

