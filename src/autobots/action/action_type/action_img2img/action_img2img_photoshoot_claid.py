from typing import Type, Literal
from loguru import logger
from openai.types import ImagesResponse, Image
from pydantic import ValidationError, BaseModel

from src.autobots import SettingsProvider
from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionConfigType, ActionInputType, \
    ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.claid.claid import get_claid
from src.autobots.conn.claid.claid_model import ClaidPhotoShootInputModel, ClaidErrorResponse, PhotoshootObject, PhotoshootScene, PhotoshootOutput
from src.autobots.core.utils import gen_uuid
from src.autobots.data_model.context import Context
from src.autobots.user.user_orm_model import UserORM


class ActionConfigPhotoshootClaid(BaseModel):
    number_of_images: int = 1
    format: Literal["jpeg", "png", "webp", "avif"] = "jpeg"


class ActionInputPhotoshootClaid(BaseModel):
    object: PhotoshootObject
    scene: PhotoshootScene
    output: ActionConfigPhotoshootClaid | None = None


class ActionImg2ImgPhotoshootClaid(
    ActionABC[
        ActionConfigPhotoshootClaid, ActionConfigPhotoshootClaid, ActionConfigPhotoshootClaid, ActionInputPhotoshootClaid, ImagesResponse]
):
    type = ActionType.img2img_photoshoot_claid

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return ActionConfigPhotoshootClaid

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return ActionConfigPhotoshootClaid

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return ActionConfigPhotoshootClaid

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return ActionInputPhotoshootClaid

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return ImagesResponse

    def __init__(self, action_config: ActionConfigPhotoshootClaid, user: UserORM | None = None):
        super().__init__(action_config=action_config, user=user)

    async def run_action(self, ctx: Context, action_input: ActionInputPhotoshootClaid) -> ImagesResponse | Exception:
        claid_ai = get_claid()
        if action_input.output and action_input.output.number_of_images:
            self.action_config.number_of_images = action_input.output.number_of_images
        if action_input.output and action_input.output.format:
            self.action_config.format = action_input.output.format
        settings = SettingsProvider.sget()
        destination_s3_path = f"{settings.CLAID_SIDE_S3_BUCKET}{settings.CLAID_PATH_PREFIX}{gen_uuid()}/output/"

        claid_photoshoot_input_model = ClaidPhotoShootInputModel(
            object=action_input.object,
            scene=action_input.scene,
            output=PhotoshootOutput(
                destination=destination_s3_path,
                number_of_images=self.action_config.number_of_images,
                format=self.action_config.format,
            )
        )
        try:
            res = await claid_ai.photoshoot(claid_photoshoot_input_model)
            if isinstance(res, ClaidErrorResponse):
                return Exception(res.model_dump(exclude_none=True))
            elif isinstance(res, Exception):
                return res
            elif isinstance(res, list):
                images = [Image(url=image_url) for image_url in res]
                image_res = ImagesResponse(created=1, data=images)
                return image_res
        except ValidationError | Exception as e:
            logger.error(str(e))
            return Exception(str(e))
