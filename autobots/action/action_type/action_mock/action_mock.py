from typing import Any

from autobots.action.action.common_action_models import TextObj
from autobots.action.action_type.abc.IAction import IAction


class MockAction(IAction[Any, TextObj, TextObj]):

    def __init__(self, action_config: Any = None):
        self.action_config = action_config

    async def run_action(self, input: TextObj) -> TextObj:
        input.text = input.text + "_result"
        return input
