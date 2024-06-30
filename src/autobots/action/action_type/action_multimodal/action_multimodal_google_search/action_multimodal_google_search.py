from typing import Type

from loguru import logger

from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionConfigType, ActionOutputType, ActionInputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_multimodal.action_multimodal_google_search.action_multimodal_google_search_model import \
    ActionMultimodalGoogleSearchConfig, ActionMultimodalGoogleSearchInput, ActionMultimodalGoogleSearchOutput
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.conn.serp.serp import get_serp


class ActionMultimodalGoogleSearch(
    ActionABC[
        ActionMultimodalGoogleSearchConfig,
        ActionMultimodalGoogleSearchConfig,
        ActionMultimodalGoogleSearchConfig,
        ActionMultimodalGoogleSearchInput,
        ActionMultimodalGoogleSearchOutput
    ]
):
    type = ActionType.multimodal_google_search

    @staticmethod
    def get_description() -> str:
        return "Do a google search"

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return ActionMultimodalGoogleSearchConfig

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return ActionMultimodalGoogleSearchConfig

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return ActionMultimodalGoogleSearchConfig

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return ActionMultimodalGoogleSearchInput

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return ActionMultimodalGoogleSearchOutput

    async def run_action(
            self,
            action_input: ActionMultimodalGoogleSearchInput
    ) -> ActionMultimodalGoogleSearchOutput | None:
        if action_input and action_input.text != "":
            self.action_config.q += action_input.text
        google_search_api = get_serp().serp_google_search
        result_or_exception = await google_search_api.search(self.action_config)
        if isinstance(result_or_exception, Exception):
            logger.error(str(result_or_exception))
            return None
        return result_or_exception

    @staticmethod
    async def run_tool(
            action_config: ActionMultimodalGoogleSearchConfig
    ) -> ActionMultimodalGoogleSearchOutput:
        action = ActionMultimodalGoogleSearch(action_config)
        input = ActionMultimodalGoogleSearchInput(text="")
        output = await action.run_action(input)
        return output
