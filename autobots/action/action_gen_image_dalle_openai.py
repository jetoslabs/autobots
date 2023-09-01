from typing import List

from autobots.action.action_doc_model import ActionDoc, ActionCreate
from autobots.action.action_types import ActionType
from autobots.conn.openai.image_model import ImageRes, ImageReq
from autobots.conn.openai.openai import get_openai
from autobots.prompts.user_prompts import Input


class ActionCreateGenImageDalleOpenai(ActionCreate):
    type: ActionType = ActionType.gen_image_dalle_openai
    input: ImageReq


class ActionGenImageDalleOpenai:
    type = ActionType.gen_image_dalle_openai

    def __init__(self):
        pass

    @staticmethod
    async def run(action: ActionDoc, action_input: Input) -> List[ImageRes]:
        image_req = ImageReq.model_validate(action.input)
        image_req.prompt = action_input.input
        images = await get_openai().create_image(image_req)
        return images

    async def output_to_input(self, images: List[ImageRes]) -> Input:
        pass
