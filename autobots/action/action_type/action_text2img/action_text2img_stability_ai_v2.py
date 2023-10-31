from typing import List, Optional, Dict, Any

from autobots.action.action.action_doc_model import ActionCreate, ActionDoc
from autobots.action.action_type.abc.IAction import IAction
from autobots.action.action_type.action_types import ActionType
from autobots.action.action.common_action_models import TextObj, ImagesRes
from autobots.conn.openai.image_model import ImageRes
from autobots.conn.stability.stability import get_stability
from autobots.conn.stability.stability_data import StabilityReq

class ActionCreateGenImageStabilityAi(ActionCreate):
    type: ActionType = ActionType.text2img_stability_ai
    config: StabilityReq
    input: Optional[TextObj] = None
    output: Optional[ImagesRes] = None


class ActionGenImageStabilityAiV2(IAction[StabilityReq, TextObj, ImagesRes]):
    type = ActionType.text2img_stability_ai

    def __init__(self, action_config: StabilityReq):
        super().__init__(action_config)

    @staticmethod
    async def run_action_doc(action_doc: ActionDoc, action_input_dict: Dict[str, Any]) -> ImagesRes:
        action = ActionGenImageStabilityAiV2(StabilityReq.model_validate(action_doc.config))
        action_output = await action.run_action(TextObj.model_validate(action_input_dict))
        return action_output

    async def run_action(self, action_input: TextObj) -> ImagesRes:
        self.action_config.prompt = f"{self.action_config.prompt}\n{action_input.text}"
        file_url = await get_stability().text_to_image(self.action_config)
        images = [ImageRes(url=file_url.unicode_string())]
        return ImagesRes(images=images)

    async def invoke_action(self, input_str: str) -> List[ImageRes]:
        pass

    @staticmethod
    async def instruction() -> str:
        pass
