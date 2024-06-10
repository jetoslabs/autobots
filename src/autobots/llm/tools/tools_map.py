from typing import Literal

from typing_extensions import TypedDict, Required

from autobots.action.action_type.action_multimodal.action_multimodal_google_search.action_multimodal_google_search import \
    ActionMultimodalGoogleSearch
from autobots.action.action_type.action_text2text.action_text2text_read_urls import ActionText2TextReadUrl
from src.autobots.action.action_type.action_text2text.action_text2text_search_web import ActionText2TextSearchWeb


class ActionTools(TypedDict, total=False):
    type: Required[Literal[
        "search_web",
        "read_url",
        "google_search"
    ]]


TOOLS_MAP = {
    "search_web": ActionText2TextSearchWeb,
    "read_url": ActionText2TextReadUrl,
    "google_search": ActionMultimodalGoogleSearch
}
