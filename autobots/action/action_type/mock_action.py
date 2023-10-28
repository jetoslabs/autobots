from autobots.action.action.common_action_models import TextObj


class MockAction():

    def __init__(self, action_config=None):
        self.action_config = action_config

    async def run_action(self, input: TextObj = TextObj(text="mock action")) -> TextObj:
        input.text = input.text + "_result"
        return input
