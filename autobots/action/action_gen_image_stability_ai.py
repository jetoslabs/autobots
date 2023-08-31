from typing import List

from autobots.action.action_doc_model import ActionDoc, ActionCreate
from autobots.action.action_types import ActionType
from autobots.conn.openai.image_model import ImageRes
from autobots.conn.stability.stability import get_stability
from autobots.conn.stability.stability_data import StabilityReq
from autobots.prompts.user_prompts import Input


class ActionCreateGenImageStabilityAi(ActionCreate):
    type: ActionType = ActionType.gen_image_stability_ai
    input: StabilityReq


class ActionGenImageStabilityAi:
    type = ActionType.gen_image_stability_ai

    def __init__(self):
        pass

    @staticmethod
    async def run(action: ActionDoc, action_input: Input) -> List[ImageRes]:
        stability_req = StabilityReq.model_validate(action.input)
        stability_req.prompt = action_input.input
        file_url = await get_stability().text_to_image(stability_req)
        resp = [ImageRes(url=file_url.unicode_string())]
        return resp

    async def output_to_input(self, images: List[ImageRes]) -> Input:
        pass
