from typing import TypeVar, Generic

from pydantic import BaseModel

from autobots.action.action.action_doc_model import ActionDoc
from autobots.action.action_result.action_result_doc_model import ActionResultCreate, ActionResultStatus, \
    ActionResultUpdate, ActionResultDoc
from autobots.action.action_result.user_action_result import UserActionResult
from autobots.core.log import log

ActionConfigType = TypeVar("ActionConfigType", bound=BaseModel)
ActionInputType = TypeVar("ActionInputType", bound=BaseModel)
ActionOutputType = TypeVar("ActionOutputType", bound=BaseModel)


class IAction(Generic[ActionConfigType, ActionInputType, ActionOutputType]):

    def __init__(self, action_config: ActionConfigType):
        self.action_config = action_config

    async def run_action(self, action_input: ActionInputType) -> ActionOutputType:
        raise NotImplementedError

    async def run_action_in_background(
            self,
            action_doc: ActionDoc,
            user_action_result: UserActionResult,
            action_input: ActionInputType
    ) -> ActionResultDoc | None:
        action_doc.input = action_input
        action_result_create = ActionResultCreate(status=ActionResultStatus.processing, action=action_doc)
        action_result_doc = await user_action_result.create_action_result(action_result_create)
        try:
            result = await self.run_action(action_input)
            action_result_doc.status = ActionResultStatus.success
            action_result_doc.action.output = result
            log.bind(action_result_doc=action_result_doc).info("Action run success")
        except Exception as e:
            action_result_doc.status = ActionResultStatus.error
            log.bind(action_result_doc=action_result_doc, error=e).error("Action run error")
        finally:
            action_result_doc = await user_action_result.update_action_result(
                action_result_doc.id,
                ActionResultUpdate(**action_result_doc.model_dump())
            )
            log.bind(action_result_doc=action_result_doc).info("Action Result updated")
        return action_result_doc
