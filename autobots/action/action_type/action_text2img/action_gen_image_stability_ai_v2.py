from typing import List, Optional

from autobots.action.action_type.abc.IActionGenImage import IActionGenImage
from autobots.action.action.action_doc_model import ActionCreate
from autobots.action.action_type.action_types import ActionType
from autobots.action.action.common_action_models import TextObj
from autobots.conn.openai.image_model import ImageRes
from autobots.conn.stability.stability import get_stability
from autobots.conn.stability.stability_data import StabilityReq

class ActionCreateGenImageStabilityAi(ActionCreate):
    type: ActionType = ActionType.gen_image_stability_ai
    config: StabilityReq
    input: Optional[TextObj] = None
    output: Optional[List[ImageRes]] = None


class ActionGenImageStabilityAiV2(IActionGenImage):
    type = ActionType.gen_image_stability_ai

    def __init__(self, action_data: StabilityReq):
        self.stability_req = action_data

    async def run_action(self, action_input: TextObj) -> List[ImageRes]:
        self.stability_req.prompt = f"{self.stability_req.prompt}\n{action_input.text}"
        file_url = await get_stability().text_to_image(self.stability_req)
        resp = [ImageRes(url=file_url.unicode_string())]
        return resp

    async def invoke_action(self, input_str: str) -> List[ImageRes]:
        pass

    @staticmethod
    async def instruction() -> str:
        pass
