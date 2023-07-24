from typing import Dict, List

from pydantic import HttpUrl

from autobots.action.action import Action, ActionData
from autobots.conn.selenium.selenium import get_selenium


class ReadUrlsData(ActionData):
    read_urls_req: List[HttpUrl]
    context: Dict[HttpUrl, str] = {}


class ReadUrls(Action):

    async def run(self, action_data: ReadUrlsData, *args, **kwargs):
        for url in action_data.read_urls_req:
            action_data.context[url] = await get_selenium().read_url_text(url)
        return action_data  # Don't return action_data as it is not new, same input object is modified
