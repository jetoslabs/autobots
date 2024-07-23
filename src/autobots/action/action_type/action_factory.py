from functools import lru_cache
from typing import List, Any, Dict

from fastapi import BackgroundTasks, HTTPException
from loguru import logger
from pydantic import BaseModel

from src.autobots.action.action.action_doc_model import ActionDoc, ActionResult
from src.autobots.action.action.common_action_models import TextObj
from src.autobots.action.action_result.action_result_doc_model import ActionResultDoc, ActionResultCreate, \
    ActionResultUpdate
from src.autobots.action.action_result.user_action_result import UserActionResult
from src.autobots.action.action_type.abc.ActionABC import ActionConfigType
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


class RunActionObj(BaseModel):
    config_dict: Dict[str, Any]
    input_dict: Dict[str, Any]
    output_dict: Dict[str, Any]


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
            if not action_class:
                raise Exception(f"Action {action_type} not found in ACTION_MAP")
            config_create = action_class.get_config_create_type().model_validate(action_config_create)
            config = await action_class.create_config(config_create)
            return config
        except Exception as e:
            logger.error(str(e))
            raise

    @staticmethod
    async def update_action_config(
            action_type: ActionType, action_config: Dict[str, Any], action_config_update: Dict[str, Any]
    ) -> ActionConfigType:
        try:
            action_class = ACTION_MAP.get(action_type)
            if not action_class:
                raise Exception(f"Action {action_type} not found in ACTION_MAP")
            config = action_class.get_config_type().model_validate(action_config)
            config_update = action_class.get_config_update_type().model_validate(action_config_update)
            updated_config = await action_class.update_config(config, config_update)
            return updated_config
        except Exception as e:
            logger.error(str(e))
            raise

    @staticmethod
    async def delete_action_config(
            action_type: ActionType, action_config: Dict[str, Any]
    ) -> ActionConfigType:
        try:
            action_class = ACTION_MAP.get(action_type)
            if not action_class:
                raise Exception(f"Action {action_type} not found in ACTION_MAP")
            config = action_class.get_config_type().model_validate(action_config)
            deleted_config = await action_class.delete_config(config)
            return deleted_config
        except Exception as e:
            logger.error(str(e))
            raise

    @staticmethod
    async def run_action(action_doc: ActionDoc, action_input_dict: Dict[str, Any]) -> RunActionObj | Exception:
        try:
            action = ACTION_MAP.get(action_doc.type)
            if not action:
                logger.error(f"Action {action_doc.type} not found in ACTION_MAP")
                raise Exception(f"Action {action_doc.type} not found in ACTION_MAP")
            config = action.get_config_type().model_validate(action_doc.config)
            prev_results: List[ActionResult] | None = action_doc.results
            updated_config = await action.update_config_with_prev_results(config, prev_results)
            input = action.get_input_type().model_validate(action_input_dict)
            output = await action(updated_config).run_action(input)

            if isinstance(output, Exception):
                return output

            return RunActionObj(
                config_dict=updated_config.model_dump(exclude_none=True),
                input_dict=input.model_dump(exclude_none=True),
                output_dict=output.model_dump(exclude_none=True),
            )
        except Exception as e:
            logger.error(str(e))
            raise

    @staticmethod
    async def run_action_in_background(
            action_doc: ActionDoc,
            action_input_dict: Dict[str, Any],
            user_action_result: UserActionResult,
            action_result_id: str = None,
            background_tasks: BackgroundTasks = None,
            webhook: Webhook | None = None,
    ) -> ActionResultDoc | None:
        action_result_doc: ActionResultDoc | None = None
        if action_result_id is not None:
            action_result_doc = await user_action_result.get_action_result(action_result_id)
            if action_result_doc is None:
                logger.error(f"Action Result not found {action_result_id}")
                raise HTTPException(status_code=400, detail="Action Result not found")
            # Change status back to processing
            action_result_update: ActionResultUpdate = ActionResultUpdate(status=EventResultStatus.processing)
            action_result_doc = await user_action_result.update_action_result(action_result_id, action_result_update)
        else:
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
                ActionFactory._run_action_as_background_task, action_input_dict, action_result_doc, user_action_result,
                webhook
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
            run_action_obj: RunActionObj = await ActionFactory.run_action(action_result_doc.result, action_input_dict)
            # Action is a success
            # Update ActionDoc model config, input and output
            action_result_doc.status = EventResultStatus.success
            action_result_doc.error_message = None
            action_result_doc.result.config = run_action_obj.config_dict
            action_result_doc.result.input = run_action_obj.input_dict
            action_result_doc.result.output = run_action_obj.output_dict
            if action_result_doc.result.results is None:
                action_result_doc.result.results = []
            action_result_doc.result.results.append(
                ActionResult(input=run_action_obj.input_dict, output=run_action_obj.output_dict))
            logger.bind(action_result_doc=action_result_doc).info("Action run success")
        except Exception as e:
            # Action resulted in an error
            action_result_doc.status = EventResultStatus.error
            action_result_doc.error_message = TextObj(text=str(e))
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
