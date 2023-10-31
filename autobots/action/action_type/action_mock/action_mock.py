from typing import Dict, Any

from autobots.action.action.action_doc_model import ActionDoc
from autobots.action.action.common_action_models import TextObj
from autobots.action.action_type.abc.IAction import IAction


class MockAction(IAction[TextObj, TextObj, TextObj]):

    def __init__(self, action_config: TextObj):
        super().__init__(action_config)

    @staticmethod
    async def run_action_doc(action_doc: ActionDoc, action_input_dict: Dict[str, Any]) -> TextObj:
        action = MockAction(TextObj.model_validate(action_doc.config))
        action_output = await action.run_action(TextObj.model_validate(action_input_dict))
        return action_output

    async def run_action(self, action_input: TextObj) -> TextObj:
        output = TextObj(
            text=f"Config_{self.action_config.text}+Input_{action_input.text}+Output"
        )
        return output
