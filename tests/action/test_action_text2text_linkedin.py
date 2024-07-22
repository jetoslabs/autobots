import pytest

from src.autobots.action.action_type.action_text2text.action_text2text_linkedin import LinkedInReq, ActionLinkedInScrape
import asyncio

@pytest.mark.asyncio
async def test_action_text2text_linkedin_happy_path(set_test_settings):
    config = LinkedInReq(linkedin_id="sample_linkedin_id")
    input = LinkedInReq(linkedin_id="sample_linkedin_id")
    profile_data = await ActionLinkedInScrape(action_config=config).run_action(input)
    print(profile_data)
