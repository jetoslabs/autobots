from typing import List, Optional, Dict, Any

from autobots.action.action_type.abc.IAction import IAction
from autobots.action.action.action_doc_model import ActionCreate, ActionDoc
from autobots.action.action_type.action_types import ActionType
from autobots.action.action.common_action_models import TextObj, ImagesRes
from autobots.conn.openai.image_model import ImageRes, ImageReq
from autobots.conn.openai.openai import get_openai


class ActionCreateGenImageDalleOpenai(ActionCreate):
    type: ActionType = ActionType.text2img_dalle_openai
    config: ImageReq
    input: Optional[TextObj] = None
    output: Optional[ImagesRes] = None


class ActionGenImageDalleOpenAiV2(IAction[ImageReq, TextObj, ImagesRes]):
    type = ActionType.text2img_dalle_openai

    def __init__(self, action_config: ImageReq):
        super().__init__(action_config)

    @staticmethod
    async def run_action_doc(action_doc: ActionDoc, action_input_dict: Dict[str, Any]) -> ImagesRes:
        action = ActionGenImageDalleOpenAiV2(ImageReq.model_validate(action_doc.config))
        action_output = await action.run_action(TextObj.model_validate(action_input_dict))
        return action_output

    async def run_action(self, action_input: TextObj) -> ImagesRes:
        self.action_config.prompt = f"{self.action_config.prompt}\n{action_input.text}"
        images = await get_openai().create_image(self.action_config)
        return ImagesRes(images=images)

    async def invoke_action(self, input_str: str) -> List[ImageRes]:
        pass

    @staticmethod
    async def instruction() -> str:
        pass
