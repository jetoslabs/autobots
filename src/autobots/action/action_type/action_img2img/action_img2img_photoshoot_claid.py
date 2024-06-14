from typing import Type
from loguru import logger
from openai.types import ImagesResponse, Image
from pydantic import ValidationError

from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.claid.claid import get_claid
from src.autobots.conn.claid.claid_model import ClaidPhotoShootRequestModel, \
    ClaidPhotoShootInputModel, ClaidErrorResponse


class ActionImg2ImgPhotoshootClaid(
    ActionABC[ClaidPhotoShootRequestModel, ClaidPhotoShootRequestModel, ClaidPhotoShootRequestModel, ClaidPhotoShootInputModel, ImagesResponse]
):
    type = ActionType.img2img_photoshoot_claid

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return ClaidPhotoShootRequestModel

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return ClaidPhotoShootRequestModel

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return ClaidPhotoShootRequestModel

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return ClaidPhotoShootInputModel

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return ImagesResponse

    def __init__(self, action_config: ClaidPhotoShootRequestModel):
        super().__init__(action_config)

    async def run_action(self, action_input: ClaidPhotoShootInputModel) -> ImagesResponse | Exception:
        claid_ai = get_claid()
        if self.action_config.output:
            action_input.output = self.action_config.output
        try:
            res = await claid_ai.photoshoot(action_input)
            if isinstance(res, ClaidErrorResponse):
                return Exception(res.model_dump(exclude_none=True))
            elif isinstance(res, Exception):
                return res
            elif isinstance(res, list):
                images = [Image(url=image_url) for image_url in res]
                image_res = ImagesResponse(created=1, images=images)
                return image_res
        except ValidationError | Exception as e:
            logger.error(str(e))
            return Exception(str(e))
