from typing import List

from autobots.action.IActionGenImage import IActionGenImage
from autobots.action.action_doc_model import ActionCreate
from autobots.action.action_types import ActionType
from autobots.conn.openai.image_model import ImageRes, ImageReq
from autobots.conn.openai.openai import get_openai
from autobots.prompts.user_prompts import Input


class ActionCreateGenImageDalleOpenai(ActionCreate):
    type: ActionType = ActionType.gen_image_dalle_openai
    input: ImageReq


class ActionGenImageDalleOpenAiV2(IActionGenImage):
    type = ActionType.gen_image_dalle_openai

    def __init__(self, action_data: ImageReq):
        self.image_req = action_data

    async def run_action(self, action_input: Input) -> List[ImageRes]:
        self.image_req.prompt = action_input.input
        images = await get_openai().create_image(self.image_req)
        return images

    async def invoke_action(self, input_str: str) -> List[ImageRes]:
        pass

    @staticmethod
    async def instruction() -> str:
        pass
