import asyncio
from typing import Type, Dict, Any
from loguru import logger
from pydantic import BaseModel
from src.autobots.conn.linkedin_scraper.linkedin_scraper import get_linkedin_scrape
from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType

class LinkedInReq(BaseModel):
    linkedin_id: str

class LinkedInRes(BaseModel):
    profile_data: Dict[str, Any]

class ActionLinkedInScrape(
    ActionABC[LinkedInReq, LinkedInReq, LinkedInReq, LinkedInRes, Dict[str, Any]]
):
    type = ActionType.action_linkedin

    @staticmethod
    def get_config_create_type() -> Type[ActionConfigCreateType]:
        return LinkedInReq

    @staticmethod
    def get_config_update_type() -> Type[ActionConfigUpdateType]:
        return LinkedInReq

    @staticmethod
    def get_config_type() -> Type[ActionConfigType]:
        return LinkedInReq

    @staticmethod
    def get_input_type() -> Type[ActionInputType]:
        return LinkedInRes

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return Dict[str, Any]

    def __init__(self, action_config: LinkedInReq):
        super().__init__(action_config)

    async def run_action(self, action_input: LinkedInRes) -> Dict[str, Any] | None:
        try:
            if not self.action_config.linkedin_id:
                return None
            profile_data = await asyncio.to_thread(get_linkedin_scrape, self.action_config.linkedin_id)
            return profile_data
        except Exception as e:
            logger.error(f"Error in running LinkedIn scrape action: {e}")
            return None
