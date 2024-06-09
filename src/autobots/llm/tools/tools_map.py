from typing import Literal

from typing_extensions import TypedDict, Required

from autobots.action.action_type.action_text2text.action_text2text_read_urls import ActionText2TextReadUrl
from src.autobots.action.action_type.action_text2text.action_text2text_search_web import ActionText2TextSearchWeb


class ActionTools(TypedDict, total=False):
    type: Required[Literal[
        "search_web",
        "read_url",
    ]]


TOOLS_MAP = {
    "search_web": ActionText2TextSearchWeb,
    "read_url": ActionText2TextReadUrl,
}
