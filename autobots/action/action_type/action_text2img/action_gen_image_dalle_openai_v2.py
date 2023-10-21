from typing import List, Optional

from autobots.action.action_type.IActionGenImage import IActionGenImage
from autobots.action.action_doc_model import ActionCreate
from autobots.action.action_type.action_types import ActionType
from autobots.conn.openai.image_model import ImageRes, ImageReq
from autobots.conn.openai.openai import get_openai
from autobots.prompts.user_prompts import TextObj


class ActionCreateGenImageDalleOpenai(ActionCreate):
    type: ActionType = ActionType.gen_image_dalle_openai
    config: ImageReq
    input: Optional[TextObj] = None
    output: Optional[List[ImageRes]] = None


class ActionGenImageDalleOpenAiV2(IActionGenImage):
    type = ActionType.gen_image_dalle_openai

    def __init__(self, action_data: ImageReq):
        self.image_req = action_data

    async def run_action(self, action_input: TextObj) -> List[ImageRes]:
        self.image_req.prompt = f"{self.image_req.prompt}\n{action_input.text}"
        images = await get_openai().create_image(self.image_req)
        return images

    async def invoke_action(self, input_str: str) -> List[ImageRes]:
        pass

    @staticmethod
    async def instruction() -> str:
        pass
