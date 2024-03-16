from typing import Type, Optional
from loguru import logger
from pydantic import BaseModel, Field, ValidationError

from src.autobots.action.action_type.abc.IAction import IAction, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.claid.claid import get_calid_ai
from src.autobots.conn.claid.claid_model import ClaidRequestModel, ClaidResponse, ClaidErrorResponse


class ActionImg2BulkEditClaid(
    IAction[ClaidRequestModel, ClaidRequestModel, ClaidRequestModel, ClaidRequestModel, ClaidResponse]
):
    type = ActionType.img2img_bulk_edit_claid

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return ClaidRequestModel

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return ClaidRequestModel

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return ClaidRequestModel

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return ClaidRequestModel

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return ClaidResponse

    def __init__(self, action_config: ClaidRequestModel):
        super().__init__(action_config)

    async def run_action(self, action_input: ClaidRequestModel) -> ClaidResponse | ClaidErrorResponse:
        claidai = get_calid_ai()
        try:
            res = await claidai.bulkEdit(action_input)
            return res
        except ValidationError as e:
            logger.error(str(e))
        except Exception as e:
            logger.error(str(e))

        return res
