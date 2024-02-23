from functools import lru_cache
from typing import List, Any, Dict

from fastapi import BackgroundTasks
from loguru import logger
from pydantic import BaseModel

from src.autobots.action.action.action_doc_model import ActionDoc
from src.autobots.action.action.common_action_models import TextObj
from src.autobots.action.action_result.action_result_doc_model import ActionResultDoc, ActionResultCreate, \
    ActionResultUpdate
from src.autobots.action.action_result.user_action_result import UserActionResult
from src.autobots.action.action_type.abc.IAction import ActionConfigType
from src.autobots.action.action_type.action_map import ACTION_MAP
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.api.webhook import Webhook
from src.autobots.event_result.event_result_model import EventResultStatus


class ActionDataTypes(BaseModel):
    type: ActionType
    config_create: Dict[str, Any] | None = None
    config_update: Dict[str, Any] | None = None
    config: Dict[str, Any] | None = None
    input: Dict[str, Any] | None = None
    output: Dict[str, Any] | None = None


class ActionFactory:

    @staticmethod
    @lru_cache
    def get_action_types() -> List[str]:
        action_types = [action_type for action_type in ActionType if not action_type.lower().startswith("mock")]
        return action_types

    @staticmethod
    async def get_data_types(
            action_type: ActionType,
            is_get_config_create: bool = True,
            is_get_config_update: bool = True,
            is_get_config: bool = True,
            is_get_input: bool = True,
            is_get_output: bool = True
    ) -> ActionDataTypes:
        try:
            action_data_types = ActionDataTypes(type=action_type)
            action = ACTION_MAP.get(action_type)
            if action:
                if is_get_config_create:
                    action_data_types.config_create = action.get_config_create_type().model_json_schema()
                if is_get_config_update:
                    action_data_types.config_update = action.get_config_update_type().model_json_schema()
                if is_get_config:
                    action_data_types.config = action.get_config_type().model_json_schema()
                if is_get_input:
                    action_data_types.input = action.get_input_type().model_json_schema()
                if is_get_output:
                    action_data_types.output = action.get_output_type().model_json_schema()
            return action_data_types
        except Exception as e:
            logger.error(f"ActionType does not exist {action_type}, error: {str(e)}")
            raise

    @staticmethod
    async def create_action_config(action_type: ActionType, action_config_create: Dict[str, Any]) -> ActionConfigType:
        try:
            action_class = ACTION_MAP.get(action_type)
            config_create = action_class.get_config_create_type().model_validate(action_config_create)
            config = await action_class.create_config(config_create)
            return config
        except Exception:
            raise

    @staticmethod
    async def update_action_config(
            action_type: ActionType, action_config: Dict[str, Any], action_config_update: Dict[str, Any]
    ) -> ActionConfigType:
        try:
            action_class = ACTION_MAP.get(action_type)
            config = action_class.get_config_type().model_validate(action_config)
            config_update = action_class.get_config_update_type().model_validate(action_config_update)
            updated_config = await action_class.update_config(config, config_update)
            return updated_config
        except Exception:
            raise

    @staticmethod
    async def delete_action_config(
            action_type: ActionType, action_config: Dict[str, Any]
    ) -> ActionConfigType:
        try:
            action_class = ACTION_MAP.get(action_type)
            config = action_class.get_config_type().model_validate(action_config)
            deleted_config = await action_class.delete_config(config)
            return deleted_config
        except Exception:
            raise

    @staticmethod
    async def run_action(action_doc: ActionDoc, action_input_dict: Dict[str, Any]) -> Any:
        action = ACTION_MAP.get(action_doc.type)
        config = action.get_config_type().model_validate(action_doc.config)
        input = action.get_input_type().model_validate(action_input_dict)
        output = await action(config).run_action(input)
        return output.model_dump()

    @staticmethod
    async def run_action_in_background(
            action_doc: ActionDoc,
            action_input_dict: Dict[str, Any],
            user_action_result: UserActionResult,
            background_tasks: BackgroundTasks = None,
            webhook: Webhook | None = None,
    ) -> ActionResultDoc | None:
        # Create initial Action Result
        action_doc.input = action_input_dict
        action_result_create: ActionResultCreate = ActionResultCreate(
            status=EventResultStatus.processing, result=action_doc, is_saved=False
        )
        action_result_doc = await user_action_result.create_action_result(action_result_create)
        # Run Action in background and update the Action Result with Output
        if background_tasks:
            # Run in background
            background_tasks.add_task(
                ActionFactory._run_action_as_background_task, action_input_dict, action_result_doc, user_action_result, webhook
            )
        else:
            # For testing
            await ActionFactory._run_action_as_background_task(
                action_input_dict, action_result_doc, user_action_result, webhook
            )
        return action_result_doc

    @staticmethod
    async def _run_action_as_background_task(
            action_input_dict: Dict[str, Any],
            action_result_doc: ActionResultDoc,
            user_action_result: UserActionResult,
            webhook: Webhook | None = None,
    ) -> None:
        try:
            # Run the action
            result = await ActionFactory.run_action(action_result_doc.result, action_input_dict)
            # Action is a success
            action_result_doc.status = EventResultStatus.success
            action_result_doc.result.output = result
            logger.bind(action_result_doc=action_result_doc).info("Action run success")
        except Exception as e:
            # Action resulted in an error
            action_result_doc.status = EventResultStatus.error
            action_result_doc.error_message = TextObj(text="Action run error")
            logger.bind(action_result_doc=action_result_doc, error=e).error("Action run error")
        finally:
            # Finally persist the Action Result
            action_result_update = ActionResultUpdate(**action_result_doc.model_dump())
            action_result_doc = await user_action_result.update_action_result(
                action_result_doc.id,
                action_result_update
            )
            logger.bind(action_result_doc=action_result_doc).info("Action Result updated")
            # Send webhook
            if webhook:
                await webhook.send(action_result_doc.model_dump())
