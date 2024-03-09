from typing import Type
from loguru import logger
from pydantic import ValidationError

from src.autobots.action.action_type.abc.IAction import IAction, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.claid.claid import get_calid_ai
from src.autobots.conn.claid.claid_model import ClaidRequestModel, ClaidResponse, \
    ClaidPhotoShootOutputModel, ClaidPhotoShootRequestModel


class ActionImg2ImgPhotoshootClaid(
    IAction[ClaidPhotoShootRequestModel, ClaidPhotoShootRequestModel, ClaidPhotoShootRequestModel, ClaidPhotoShootRequestModel, ClaidPhotoShootOutputModel]
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
        return ClaidPhotoShootRequestModel

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return ClaidPhotoShootOutputModel

    def __init__(self, action_config: ClaidRequestModel):
        super().__init__(action_config)

    async def run_action(self, action_input: ClaidPhotoShootRequestModel) -> ClaidPhotoShootOutputModel:
        claidAi = get_calid_ai()
        try:
            res: ClaidResponse = claidAi.photoshoot(action_input)
        except ValidationError as e:
            logger.error(str(e))
        except Exception as e:
            logger.error(str(e))

        return res
