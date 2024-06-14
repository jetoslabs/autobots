from typing import Type
from loguru import logger
from pydantic import ValidationError

from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.claid.claid import get_claid
from src.autobots.conn.claid.claid_model import ClaidPhotoShootOutputModel, ClaidPhotoShootRequestModel, \
    ClaidPhotoShootInputModel, ClaidErrorResponse


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

    async def run_action(self, action_input: ClaidPhotoShootInputModel) -> ClaidPhotoShootOutputModel | Exception:
        claid_ai = get_claid()
        if self.action_config.output:
            action_input.output = self.action_config.output
        try:
            res = await claid_ai.photoshoot(action_input)
            if isinstance(res, ClaidErrorResponse):
                return Exception(res.model_dump(exclude_none=True))
            else:
                return res
        except ValidationError as e:
            logger.error(str(e))
            return Exception(str(e))
        except Exception as e:
            logger.error(str(e))
            return Exception(str(e))
