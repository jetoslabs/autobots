from loguru import logger
from serpapi import GoogleSearch

from autobots.conn.serp.serp_google_search_response_model import SearchResponse
from autobots.conn.serp.serp_search_request import SerpGoogleSearchParams


class SerpGoogleSearch:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search(self, params: SerpGoogleSearchParams) -> SearchResponse | Exception:
        try:
            complete_params = {
                **params.model_dump(exclude_none=True),
                "api_key": self.api_key
            }
            search = GoogleSearch(complete_params)
            search_dict = search.get_dict()
            search_res = SearchResponse.model_validate(search_dict)
            return search_res
        except Exception as e:
            logger.error(str(e))
            return e
