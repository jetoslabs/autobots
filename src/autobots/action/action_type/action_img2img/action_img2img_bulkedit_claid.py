from typing import Type
from loguru import logger
from pydantic import ValidationError

from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.claid.claid import get_claid
from src.autobots.conn.claid.claid_model import ClaidBulkEditRequestModel, ClaidBulkEditResponse, ClaidErrorResponse, ClaidInputModel
from src.autobots.user.user_orm_model import UserORM


class ActionImg2BulkEditClaid(
    ActionABC[ClaidBulkEditRequestModel, ClaidBulkEditRequestModel, ClaidBulkEditRequestModel, ClaidInputModel, ClaidBulkEditResponse]
):
    type = ActionType.img2img_bulk_edit_claid

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return ClaidBulkEditRequestModel

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return ClaidBulkEditRequestModel

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return ClaidBulkEditRequestModel

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return ClaidInputModel

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return ClaidBulkEditResponse

    def __init__(self, action_config: ClaidBulkEditRequestModel, user: UserORM | None = None):
        super().__init__(action_config=action_config, user=user)

    async def run_action(self, action_input: ClaidInputModel) -> ClaidBulkEditResponse | ClaidErrorResponse:

        claidai = get_claid()
        if action_input.operations:
            self.action_config.operations = action_input.operations

        try:
            res = await claidai.bulk_edit(self.action_config)
            return res
        except ValidationError as e:
            logger.error(str(e))
        except Exception as e:
            logger.error(str(e))

        return res
