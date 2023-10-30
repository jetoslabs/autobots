from autobots.action.action.common_action_models import TextObj
from autobots.action.action_type.abc.IAction import IAction


class MockAction(IAction[TextObj, TextObj, TextObj]):

    def __init__(self, action_config: TextObj):
        super().__init__(action_config)

    async def run_action(self, action_input: TextObj) -> TextObj:
        output = TextObj(
            text=f"Config_{self.action_config.text}+Input_{action_input.text}+Output"
        )
        return output
