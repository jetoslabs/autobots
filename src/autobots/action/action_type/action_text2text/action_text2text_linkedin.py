import asyncio
from typing import Type, Dict, Any, List
from loguru import logger
from pydantic import BaseModel
from src.autobots.conn.linkedin_scraper.linkedin_scraper import get_linkedin_scrape
from src.autobots.action.action_type.abc.ActionABC import ActionABC, ActionConfigType, ActionInputType, ActionOutputType, \
    ActionConfigUpdateType, ActionConfigCreateType
from src.autobots.action.action_type.action_types import ActionType
from src.autobots.user.user_orm_model import UserORM


class LinkedInReq(BaseModel):
    linkedin_id: List[str]

class LinkedInRes(BaseModel):
    profile_data: List[Dict[str, Any]]

class ActionLinkedInScrape(
    ActionABC[LinkedInReq, LinkedInReq, LinkedInReq, LinkedInReq, LinkedInRes]
):
    type = ActionType.action_text2text_linkedin

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
        return LinkedInReq

    @staticmethod
    def get_output_type() -> Type[ActionOutputType]:
        return LinkedInRes

    def __init__(self, action_config: LinkedInReq, user: UserORM | None = None):
        super().__init__(action_config=action_config, user=user)

    async def run_action(self, action_input: LinkedInReq) -> LinkedInRes | None:
        try:
            if not self.action_config.linkedin_id:
                return None
            profile_data = await asyncio.to_thread(get_linkedin_scrape, action_input.linkedin_id)
            return LinkedInRes(profile_data=profile_data)
        except Exception as e:
            logger.error(f"Error in running LinkedIn scrape action: {e}")
            return None
