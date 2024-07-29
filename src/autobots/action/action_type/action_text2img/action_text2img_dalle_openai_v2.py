from typing import Optional, Type

from openai.types import ImagesResponse

from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionOutputType, ActionInputType, ActionConfigType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action.action_doc_model import ActionCreate
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.action.action.common_action_models import TextObj
from src.autobots.conn.openai.openai_images.image_model import ImageReq
from src.autobots.conn.openai.openai_client import get_openai
from src.autobots.data_model.context import Context
from src.autobots.user.user_orm_model import UserORM


class ActionCreateGenImageDalleOpenai(ActionCreate):
    type: ActionType = ActionType.text2img_dalle_openai
    config: ImageReq
    input: Optional[TextObj] = None
    output: Optional[ImagesResponse] = None


class ActionGenImageDalleOpenAiV2(ActionABC[ImageReq, ImageReq, ImageReq, TextObj, ImagesResponse]):
    type = ActionType.text2img_dalle_openai

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return ImageReq

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return ImageReq

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return ImageReq

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return TextObj

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return ImagesResponse

    def __init__(self, action_config: ImageReq, user: UserORM | None = None):
        super().__init__(action_config=action_config, user=user)

    async def run_action(self, ctx: Context, action_input: TextObj) -> ImagesResponse:
        self.action_config.prompt = f"{self.action_config.prompt}\n{action_input.text}"
        images = await get_openai().openai_images.create_image(self.action_config)
        return images
