from autobots.action.action.common_action_models import TextObj
from autobots.conn.serp.serp_google_search_response_model import SearchResponse
from autobots.conn.serp.serp_search_request import SerpGoogleSearchParams


class ActionMultimodalGoogleSearchConfig(SerpGoogleSearchParams):
    pass


class ActionMultimodalGoogleSearchInput(TextObj):
    pass


class ActionMultimodalGoogleSearchOutput(SearchResponse):
    pass
