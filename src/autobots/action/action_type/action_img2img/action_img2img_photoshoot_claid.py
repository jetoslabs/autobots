from typing import Type
from loguru import logger
from pydantic import ValidationError

from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.claid.claid import get_calid_ai
from src.autobots.conn.claid.claid_model import ClaidPhotoShootOutputModel, ClaidPhotoShootRequestModel, ClaidPhotoShootInputModel


class ActionImg2ImgPhotoshootClaid(
    ActionABC[ClaidPhotoShootRequestModel, ClaidPhotoShootRequestModel, ClaidPhotoShootRequestModel, ClaidPhotoShootInputModel, ClaidPhotoShootOutputModel]
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
        return ClaidPhotoShootOutputModel

    def __init__(self, action_config: ClaidPhotoShootRequestModel):
        super().__init__(action_config)

    async def run_action(self, action_input: ClaidPhotoShootInputModel) -> ClaidPhotoShootOutputModel:
        claidAi = get_calid_ai()
        if self.action_config.output:
            action_input.output = self.action_config.output
        try:
            res: ClaidPhotoShootOutputModel = await claidAi.photoshoot(action_input)
        except ValidationError as e:
            logger.error(str(e))
        except Exception as e:
            logger.error(str(e))
        return res
